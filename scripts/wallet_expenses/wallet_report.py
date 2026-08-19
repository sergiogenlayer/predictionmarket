#!/usr/bin/env python3
"""Fetch a wallet's activity from Etherscan V2 (Ethereum + Base) and build a
spend report: where the money went, per counterparty, category and month.

Stdlib only. Two steps:

    python wallet_report.py fetch  --address 0x... --api-key $ETHERSCAN_API_KEY
    python wallet_report.py report --address 0x... --eth-price 3200

`fetch` writes raw JSON to --data-dir; `report` reads it and writes CSV +
Markdown to --out-dir. `import-csv` accepts the explorers' own CSV exports
instead, for when no API key is available.
"""

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

API = "https://api.etherscan.io/v2/api"
PAGE = 1000
RATE_SLEEP = 0.25  # free tier: 5 calls/sec

CHAINS = {
    1: {"name": "Ethereum", "symbol": "ETH", "explorer": "https://etherscan.io"},
    8453: {"name": "Base", "symbol": "ETH", "explorer": "https://basescan.org"},
}
ACTIONS = ("txlist", "txlistinternal", "tokentx")

STABLES = {
    "USDC", "USDC.E", "USDBC", "USDT", "DAI", "PYUSD", "FDUSD",
    "LUSD", "USDE", "USDS", "GUSD", "TUSD", "EURC",  # EURC is ~1 EUR, flagged below
}
ETH_LIKE = {"ETH", "WETH"}


# --------------------------------------------------------------------------- #
# fetch
# --------------------------------------------------------------------------- #

def _get(params):
    url = f"{API}?{urllib.parse.urlencode(params)}"
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url, timeout=60) as resp:
                payload = json.load(resp)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            wait = 2 ** attempt
            print(f"  ! {exc} — retrying in {wait}s", file=sys.stderr)
            time.sleep(wait)
            continue
        message = str(payload.get("message", ""))
        result = payload.get("result")
        if payload.get("status") == "1":
            return result if isinstance(result, list) else []
        if "no transactions found" in message.lower() or "no records found" in message.lower():
            return []
        if "rate limit" in str(result).lower() or "rate limit" in message.lower():
            time.sleep(1 + attempt)
            continue
        raise SystemExit(f"Etherscan error: {message} — {result}")
    raise SystemExit(f"Etherscan unreachable after retries: {url}")


def fetch_action(chain_id, action, address, api_key):
    """Page through one endpoint, advancing by block to get past the 10k cap."""
    out, seen, start_block = [], set(), 0
    while True:
        batch = _get({
            "chainid": chain_id, "module": "account", "action": action,
            "address": address, "startblock": start_block, "endblock": 99999999,
            "page": 1, "offset": PAGE, "sort": "asc", "apikey": api_key,
        })
        time.sleep(RATE_SLEEP)
        fresh = 0
        for row in batch:
            key = json.dumps(row, sort_keys=True)
            if key in seen:
                continue
            seen.add(key)
            out.append(row)
            fresh += 1
        if len(batch) < PAGE:
            break
        last_block = int(batch[-1]["blockNumber"])
        if last_block <= start_block and fresh == 0:
            break  # a single block holds more than PAGE rows and none are new
        start_block = last_block
    return out


def cmd_fetch(args):
    api_key = args.api_key or os.environ.get("ETHERSCAN_API_KEY")
    if not api_key:
        raise SystemExit("Need --api-key or ETHERSCAN_API_KEY (free at etherscan.io/apis).")
    os.makedirs(args.data_dir, exist_ok=True)
    for chain_id in args.chains:
        for action in ACTIONS:
            print(f"fetching {CHAINS[chain_id]['name']}/{action} ...")
            rows = fetch_action(chain_id, action, args.address, api_key)
            path = os.path.join(args.data_dir, f"{chain_id}_{action}.json")
            with open(path, "w") as fh:
                json.dump(rows, fh, indent=1)
            print(f"  {len(rows)} rows -> {path}")


# --------------------------------------------------------------------------- #
# normalise
# --------------------------------------------------------------------------- #

def _dec(value, decimals):
    try:
        return Decimal(str(value)) / (Decimal(10) ** int(decimals))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal(0)


def _ts(value):
    return datetime.fromtimestamp(int(value), tz=timezone.utc)


def normalise(chain_id, action, rows, address):
    """Flatten an Etherscan endpoint into common movement records."""
    me = address.lower()
    native = CHAINS[chain_id]["symbol"]
    out = []
    for row in rows:
        sender = (row.get("from") or "").lower()
        target = (row.get("to") or "").lower()
        if sender == me and target == me:
            direction = "self"
        elif sender == me:
            direction = "out"
        elif target == me:
            direction = "in"
        else:
            continue

        if action == "tokentx":
            symbol = (row.get("tokenSymbol") or "?").upper()
            amount = _dec(row.get("value"), row.get("tokenDecimal") or 18)
            contract = (row.get("contractAddress") or "").lower()
            kind = "erc20"
        else:
            symbol, contract, kind = native, "", ("native" if action == "txlist" else "internal")
            amount = _dec(row.get("value"), 18)

        failed = row.get("isError") == "1" or row.get("txreceipt_status") == "0"
        fee = Decimal(0)
        if action == "txlist" and sender == me:
            fee = _dec(Decimal(row.get("gasUsed", 0)) * Decimal(row.get("gasPrice", 0)), 18)

        out.append({
            "chain": CHAINS[chain_id]["name"],
            "chain_id": chain_id,
            "kind": kind,
            "hash": row.get("hash"),
            "block": int(row.get("blockNumber", 0)),
            "time": _ts(row.get("timeStamp")),
            "direction": direction,
            "counterparty": target if direction in ("out", "self") else sender,
            "symbol": symbol,
            "contract": contract,
            "amount": amount,
            "fee_eth": fee,
            "method": row.get("functionName") or row.get("methodId") or "",
            "failed": failed,
        })
    return out


def load_movements(data_dir, address, chains):
    movements = []
    for chain_id in chains:
        for action in ACTIONS:
            path = os.path.join(data_dir, f"{chain_id}_{action}.json")
            if not os.path.exists(path):
                print(f"  (missing {path}, skipping)", file=sys.stderr)
                continue
            with open(path) as fh:
                movements += normalise(chain_id, action, json.load(fh), address)
    movements.sort(key=lambda m: (m["time"], m["hash"]))
    return movements


# --------------------------------------------------------------------------- #
# pricing & labelling
# --------------------------------------------------------------------------- #

def load_prices(path):
    """CSV of date,symbol,usd_price — optional manual price sheet."""
    prices = {}
    if not path:
        return prices
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            prices[(row["date"], row["symbol"].upper())] = Decimal(row["usd_price"])
    return prices


def usd_value(movement, eth_price, prices):
    symbol = movement["symbol"].upper()
    day = movement["time"].strftime("%Y-%m-%d")
    if (day, symbol) in prices:
        return movement["amount"] * prices[(day, symbol)], "price-sheet"
    if symbol in STABLES:
        return movement["amount"], "stablecoin=1.00"
    if symbol in ETH_LIKE and eth_price is not None:
        return movement["amount"] * eth_price, "flat ETH price"
    return None, "unpriced"


def load_labels(path):
    if not path or not os.path.exists(path):
        return {}
    with open(path) as fh:
        raw = json.load(fh)
    return {k.lower(): v for k, v in raw.items()}


def label_for(address, labels):
    entry = labels.get((address or "").lower())
    if isinstance(entry, dict):
        return entry.get("label", address), entry.get("category", "Uncategorised")
    if isinstance(entry, str):
        return entry, "Uncategorised"
    return address, "Uncategorised"


# --------------------------------------------------------------------------- #
# report
# --------------------------------------------------------------------------- #

def _money(value):
    return "—" if value is None else f"${value:,.2f}"


def _amount(value):
    text = f"{value:,.6f}".rstrip("0").rstrip(".")
    return text or "0"


def cmd_report(args):
    movements = load_movements(args.data_dir, args.address, args.chains)
    if not movements:
        raise SystemExit(f"No data in {args.data_dir} — run `fetch` first.")

    eth_price = Decimal(str(args.eth_price)) if args.eth_price else None
    prices = load_prices(args.price_file)
    labels = load_labels(args.labels)
    os.makedirs(args.out_dir, exist_ok=True)

    outflows = [m for m in movements if m["direction"] == "out" and m["amount"] > 0 and not m["failed"]]
    inflows = [m for m in movements if m["direction"] == "in" and m["amount"] > 0 and not m["failed"]]

    for m in movements:
        m["usd"], m["usd_basis"] = usd_value(m, eth_price, prices)
        m["label"], m["category"] = label_for(m["counterparty"], labels)

    # ---- CSV appendix -----------------------------------------------------
    csv_path = os.path.join(args.out_dir, "movements.csv")
    with open(csv_path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["date", "chain", "type", "direction", "counterparty", "label",
                         "category", "asset", "amount", "usd_value", "usd_basis",
                         "gas_fee_eth", "method", "failed", "tx"])
        for m in movements:
            writer.writerow([
                m["time"].strftime("%Y-%m-%d %H:%M:%S"), m["chain"], m["kind"], m["direction"],
                m["counterparty"], m["label"], m["category"], m["symbol"], _amount(m["amount"]),
                "" if m["usd"] is None else f"{m['usd']:.2f}", m["usd_basis"],
                _amount(m["fee_eth"]) if m["fee_eth"] else "", m["method"], "yes" if m["failed"] else "",
                f"{CHAINS[m['chain_id']]['explorer']}/tx/{m['hash']}",
            ])

    # ---- aggregates -------------------------------------------------------
    total_out = sum((m["usd"] for m in outflows if m["usd"] is not None), Decimal(0))
    total_in = sum((m["usd"] for m in inflows if m["usd"] is not None), Decimal(0))
    fees_eth = sum((m["fee_eth"] for m in movements), Decimal(0))
    fees_usd = fees_eth * eth_price if eth_price is not None else None
    unpriced = defaultdict(lambda: Decimal(0))
    for m in outflows:
        if m["usd"] is None:
            unpriced[(m["chain"], m["symbol"])] += m["amount"]

    by_counterparty = defaultdict(lambda: {"usd": Decimal(0), "count": 0, "assets": defaultdict(lambda: Decimal(0))})
    by_category = defaultdict(lambda: Decimal(0))
    by_month = defaultdict(lambda: Decimal(0))
    by_chain = defaultdict(lambda: Decimal(0))
    for m in outflows:
        bucket = by_counterparty[m["counterparty"]]
        bucket["count"] += 1
        bucket["label"], bucket["category"], bucket["chain"] = m["label"], m["category"], m["chain"]
        bucket["assets"][m["symbol"]] += m["amount"]
        if m["usd"] is not None:
            bucket["usd"] += m["usd"]
            by_category[m["category"]] += m["usd"]
            by_month[m["time"].strftime("%Y-%m")] += m["usd"]
            by_chain[m["chain"]] += m["usd"]

    # ---- Markdown ---------------------------------------------------------
    span = f"{movements[0]['time']:%Y-%m-%d} → {movements[-1]['time']:%Y-%m-%d}"
    lines = [
        f"# Wallet spend report — `{args.address}`",
        "",
        f"Chains: {', '.join(CHAINS[c]['name'] for c in args.chains)}  ",
        f"Period covered: {span}  ",
        f"Movements analysed: {len(movements)} ({len(outflows)} outgoing, {len(inflows)} incoming)",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | --- |",
        f"| Total sent out (priced) | {_money(total_out)} |",
        f"| Total received (priced) | {_money(total_in)} |",
        f"| Gas fees paid | {_amount(fees_eth)} ETH ({_money(fees_usd)}) |",
        "",
    ]
    if unpriced:
        lines += ["> Not valued in USD (no price available):", ""]
        lines += [f"> - {_amount(amt)} {sym} on {chain}" for (chain, sym), amt in sorted(unpriced.items())]
        lines += [""]

    lines += ["## Where the money went — by recipient", "",
              "| Recipient | Label | Category | Chain | Txs | Assets sent | USD |",
              "| --- | --- | --- | --- | --- | --- | --- |"]
    ranked = sorted(by_counterparty.items(), key=lambda kv: kv[1]["usd"], reverse=True)
    for addr, data in ranked[:args.top]:
        assets = ", ".join(f"{_amount(v)} {k}" for k, v in sorted(data["assets"].items()))
        lines.append(f"| `{addr}` | {data['label'] if data['label'] != addr else '—'} | "
                     f"{data['category']} | {data['chain']} | {data['count']} | {assets} | {_money(data['usd'])} |")
    if len(ranked) > args.top:
        rest = sum((d["usd"] for _, d in ranked[args.top:]), Decimal(0))
        lines.append(f"| _{len(ranked) - args.top} more recipients_ | | | | | | {_money(rest)} |")

    lines += ["", "## By category", "", "| Category | USD |", "| --- | --- |"]
    for category, amount in sorted(by_category.items(), key=lambda kv: kv[1], reverse=True):
        lines.append(f"| {category} | {_money(amount)} |")

    lines += ["", "## By chain", "", "| Chain | USD |", "| --- | --- |"]
    for chain, amount in sorted(by_chain.items(), key=lambda kv: kv[1], reverse=True):
        lines.append(f"| {chain} | {_money(amount)} |")

    lines += ["", "## By month", "", "| Month | USD |", "| --- | --- |"]
    for month, amount in sorted(by_month.items()):
        lines.append(f"| {month} | {_money(amount)} |")

    lines += ["", "## Notes", "",
              "- Stablecoins are valued 1:1 with USD; EURC is treated as 1.00 and should be "
              "restated at the EUR/USD rate if material.",
              f"- ETH valued at {'a flat ' + _money(eth_price) if eth_price is not None else 'no price — pass --eth-price'} "
              "unless a dated price sheet (`--price-file`) overrides it.",
              "- Failed transactions are excluded from totals but kept in `movements.csv`.",
              "- Internal transfers (contract-initiated ETH moves) are included.",
              "- Recipient labels come from `--labels`; edit that file to name each counterparty.",
              "- Full detail: `movements.csv`.", ""]

    md_path = os.path.join(args.out_dir, "report.md")
    with open(md_path, "w") as fh:
        fh.write("\n".join(lines))
    print(f"wrote {md_path}\nwrote {csv_path}")

    unlabelled = [a for a, d in ranked if d["label"] == a]
    if unlabelled:
        stub = os.path.join(args.out_dir, "labels.suggested.json")
        with open(stub, "w") as fh:
            json.dump({a: {"label": "", "category": ""} for a in unlabelled}, fh, indent=2)
        print(f"wrote {stub} ({len(unlabelled)} recipients still unlabelled)")


# --------------------------------------------------------------------------- #
# explorer CSV import (no API key path)
# --------------------------------------------------------------------------- #

def cmd_import_csv(args):
    """Convert an Etherscan/Basescan 'Export CSV' file into fetch-style JSON."""
    os.makedirs(args.data_dir, exist_ok=True)
    rows = []
    with open(args.csv, newline="") as fh:
        for row in csv.DictReader(fh):
            row = { (k or "").strip().strip('"'): (v or "").strip() for k, v in row.items() }
            get = lambda *names: next((row[n] for n in names if n in row and row[n] != ""), "")
            unix = get("UnixTimestamp", "Unix Timestamp", "unixtimestamp")
            value_in = get("Value_IN(ETH)", "Value_IN(ETH)")
            value_out = get("Value_OUT(ETH)", "Value_OUT(ETH)")
            value = value_out or value_in or "0"
            wei = int(Decimal(value.replace(",", "") or 0) * Decimal(10) ** 18)
            rows.append({
                "blockNumber": get("Blockno", "BlockNo", "Block Number") or "0",
                "timeStamp": unix,
                "hash": get("Transaction Hash", "Txhash"),
                "from": get("From"), "to": get("To"),
                "value": str(wei), "gasUsed": "0", "gasPrice": "0",
                "functionName": get("Method"),
                "isError": "1" if get("Status").lower().startswith("error") else "0",
            })
    path = os.path.join(args.data_dir, f"{args.chain}_{args.action}.json")
    with open(path, "w") as fh:
        json.dump(rows, fh, indent=1)
    print(f"{len(rows)} rows -> {path}")


# --------------------------------------------------------------------------- #

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    def common(p):
        p.add_argument("--address", required=True)
        p.add_argument("--chains", default="1,8453",
                       type=lambda s: [int(x) for x in s.split(",")])
        p.add_argument("--data-dir", default="wallet_data")

    fetch = sub.add_parser("fetch", help="download raw activity from Etherscan V2")
    common(fetch)
    fetch.add_argument("--api-key", default=None)
    fetch.set_defaults(func=cmd_fetch)

    report = sub.add_parser("report", help="build the CSV + Markdown spend report")
    common(report)
    report.add_argument("--out-dir", default="wallet_report")
    report.add_argument("--eth-price", default=None, help="flat USD price for ETH/WETH")
    report.add_argument("--price-file", default=None, help="CSV: date,symbol,usd_price")
    report.add_argument("--labels", default=None, help="JSON address book")
    report.add_argument("--top", type=int, default=25)
    report.set_defaults(func=cmd_report)

    imp = sub.add_parser("import-csv", help="use an explorer CSV export instead of the API")
    imp.add_argument("--csv", required=True)
    imp.add_argument("--chain", type=int, required=True, choices=sorted(CHAINS))
    imp.add_argument("--action", default="txlist", choices=ACTIONS)
    imp.add_argument("--data-dir", default="wallet_data")
    imp.set_defaults(func=cmd_import_csv)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
