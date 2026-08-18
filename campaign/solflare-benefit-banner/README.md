# Rally × Solflare — in-wallet benefit banner

Assets for the campaign benefit submitted through The Miracle
(`app.themiracle.io/campaign-checklist` → Benefit Simulator → Solflare).

## Spec compliance

| Requirement (Solflare Asset Requirements) | This asset |
| --- | --- |
| Preferred ratio 16:9 | `800×450` and `1600×900` |
| Min width 400px, 800px+ recommended | 800px / 1600px |
| Also accepted 1:1 or 4:3, subject centred | `900×900` square cut included |
| Format JPG / PNG | both provided at 800×450 |
| Safe zone: key content (logos, text) inside the centred 450×450 square | wordmark, mascot, headline, sub and CTA all sit inside it — only the gradient, grain and speed streaks bleed outside |
| Title ≤ 50 characters | see below |
| Description ≤ 700 characters | see below |

`out/proof_safezone_a.png` is a review proof with the 450×450 safe zone drawn in red.

## Files

```
out/rally_solflare_1600x900_{a,b}.png   master, @2x
out/rally_solflare_800x450_{a,b}.png    delivery size (PNG)
out/rally_solflare_800x450_{a,b}.jpg    delivery size (JPG, q92)
out/rally_solflare_900x900_{a,b}.png    1:1 fallback, subject centred
out/proof_safezone_a.png                safe-zone proof (not for delivery)
out/preview_sheet.png                   A/B comparison sheet
```

**Variant A** — brand-first: `JOIN THE RALLY` / *Prediction markets, in your wallet* / **Enter App**
**Variant B** — benefit-first: `TRADE THE FUTURE` / *Live markets · rally.fun* / **Claim your reward**

## Brand

Palette taken from rally.fun/brand:

| Token | Hex |
| --- | --- |
| Dark violet | `#25043A` |
| Rally Violet | `#6D37D5` |
| Light violet | `#E5D6FF` |
| Orange | `#FF4E00` |
| White | `#FFFFFF` |
| Black | `#000000` |

Mascot: `paloma volando 03` from the campaign Drive folder.

### Two things to swap before final delivery

1. **Wordmark** — "RALLY" is currently type-set in Archivo Condensed Black Italic as a
   stand-in. Drop the official Rally logo (SVG/PNG) into `assets/` and replace the
   `draw_tracked(... "RALLY" ...)` call in `make_banner.py` with a paste of the real lockup.
2. **Typeface** — Archivo Condensed / Archivo are open-source stand-ins for Rally's
   brand font. Point `DISPLAY` / `UI` at the licensed font files when available.

## Copy deck

### Title (≤ 50 chars)

| # | Title | Chars |
| --- | --- | --- |
| 1 | `Join the Rally — prediction markets in-wallet` | 45 |
| 2 | `Trade the future on Rally` | 25 |
| 3 | `Get [X] free credits to trade on Rally` | 38 (with the real number) |

Use #3 only once the reward is confirmed — a number in the title is what makes a
benefit card convert.

### Description (≤ 700 chars) — The Miracle template

Placeholders in `[brackets]` still need real campaign values.

```
Rally brings prediction markets straight into your Solflare wallet — pick a side, trade it, get paid when you are right.

VALUE: [e.g. $10 in trading credits + entry into the $X prize pool]

ELIGIBILITY: Active Solflare wallet users. If you don't qualify: you won't receive the credits.

STEPS:
1. Tap the link below to open Rally
2. Connect your Solflare wallet
3. [Action that unlocks the reward — e.g. place your first trade]

NEXT: [Reward] lands in your Rally account [timing, e.g. within 24h of your first trade].

See you at the Rally.
```

## Regenerating

```bash
./fetch_fonts.sh          # Archivo + Inter (SIL OFL)
pip install Pillow
python3 make_banner.py     # writes everything into out/
```

Copy lives in the `VARIANTS` dict at the top of `make_banner.py`; the headline
auto-shrinks to stay inside the safe zone, so new copy can be dropped straight in.
