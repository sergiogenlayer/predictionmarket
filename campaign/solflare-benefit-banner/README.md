# Rally — in-wallet campaign banner (theMiracle / Solflare benefit)

Creative for the Rally benefit distributed in-wallet through theMiracle
(`app.themiracle.io/campaign-checklist` → Benefit Simulator).

## Spec compliance

| Requirement | This asset |
| --- | --- |
| In-wallet banner **1080×720 px (3:2)** | `rally_inwallet_1080x720_{a,b}.png` / `.jpg` |
| All key content inside the centred **720×720 safe zone** | wordmark, mascot, headline, sub and CTA all sit inside it — only gradient, grain and speed streaks bleed into the 180 px side bands |
| **PNG or JPG**, 150 dpi recommended | both, saved with 150 dpi metadata |
| Benefit list card uses a square thumbnail | `rally_inwallet_720x720_{a,b}.png` (an exact cut of the safe zone) |
| Title ≤ 50 characters | see copy deck |
| Description: first line ≤ 70 chars (short), full text ≤ 700 chars | see copy deck |

`out/proof_safezone_a.png` is a review proof with the 720×720 safe zone outlined in red
(not for delivery).

## Files

```
out/rally_inwallet_2160x1440_{a,b}.png   master @2x
out/rally_inwallet_1080x720_{a,b}.png    delivery, PNG 150 dpi
out/rally_inwallet_1080x720_{a,b}.jpg    delivery, JPG q92 150 dpi
out/rally_inwallet_720x720_{a,b}.png     square list-card thumbnail
out/proof_safezone_a.png                 safe-zone proof
out/preview_sheet.png                    A/B comparison sheet
```

**Variant A** — brand-first: `JOIN THE RALLY` / *Prediction markets, in your wallet* / **Enter App**
**Variant B** — benefit-first: `TRADE THE FUTURE` / *Live markets · rally.fun* / **Claim your reward**

## Brand

Palette from rally.fun/brand:

| Token | Hex |
| --- | --- |
| Dark violet | `#25043A` |
| Rally Violet | `#6D37D5` |
| Light violet | `#E5D6FF` |
| Orange | `#FF4E00` |
| White | `#FFFFFF` |
| Black | `#000000` |

Mascot: `paloma volando 03` from the campaign Drive folder.

### Two placeholders to swap before final delivery

1. **Wordmark** — "RALLY" is type-set in Archivo Condensed Black Italic as a stand-in.
   Drop the official lockup into `assets/` and replace the `draw_tracked(... "RALLY" ...)`
   call in `make_banner.py` with a paste of the real file.
2. **Typeface** — Archivo Condensed / Archivo are open-source stand-ins for Rally's brand
   font; point `DISPLAY` / `UI` at the licensed files when available.

## Copy deck (Benefit Simulator fields)

Values in `[brackets]` still need the real campaign terms.

| Field | Value |
| --- | --- |
| **Title** (≤50) | `Join the Rally — prediction markets in-wallet` (45) |
| | alt: `Trade the future on Rally` (25) |
| | alt: `Get [X] free credits to trade on Rally` — use this one once the reward is confirmed; a number in the title is what makes a benefit card convert |
| **CTA Button Text** | `Enter App` (variant A) / `Claim your reward` (variant B) — keep identical to the button baked into the image |
| **Action URL** | `[rally.fun deep link for the campaign]` |
| **Category** | `Earn Rewards` (use `Claim` if the reward is a one-off claim) |
| **Provider Name** | `Rally` |
| **Image** | `rally_inwallet_1080x720_a.png` |

### Description

First line is the short description shown in the list card — it must stay ≤ 70 characters.
Full text below is 601 characters (limit 700).

```
Prediction markets, straight in your wallet. Trade with Rally.

Rally brings live prediction markets into your Solflare wallet: pick a side, trade it, get paid when you are right.

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
./fetch_fonts.sh          # Archivo + Inter (SIL OFL) — already vendored in fonts/
pip install Pillow
python3 make_banner.py    # writes every deliverable into out/
```

Copy lives in the `VARIANTS` dict at the top of `make_banner.py`; the headline auto-shrinks
to stay inside the safe zone, so new copy can be dropped straight in.
