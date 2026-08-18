# Rally × MetaMask Rewards — in-wallet banner

Creative for the Rally benefit distributed in-wallet through theMiracle
(`app.themiracle.io/campaign-checklist` → Benefit Simulator).

**Brief**: for one week Rally is featured inside MetaMask Rewards. New Rally users who
connect with MetaMask get **400 Rally Points**. Key message — *Connect with MetaMask.
Join Rally. Get 400 Rally Points.* CTA goes to **app.rally.fun**.

## Spec compliance

| Requirement | This asset |
| --- | --- |
| In-wallet banner **1080×720 px (3:2)** | `rally_inwallet_1080x720_{a,b}.png` / `.jpg` |
| All key content inside the centred **720×720 safe zone** | logo, mascot, headline, sub and CTA all sit inside it — only gradient, grain and speed streaks bleed into the 180 px side bands |
| **PNG or JPG**, 150 dpi recommended | both, with 150 dpi metadata |
| Benefit list card uses a square thumbnail | `rally_inwallet_720x720_{a,b}.png` (an exact cut of the safe zone) |
| Title ≤ 50 characters | 44 — see copy deck |
| Description: first line ≤ 70 chars (short), full text ≤ 700 | 65 / 615 — see copy deck |

`out/proof_safezone_a.png` is a review proof with the safe zone outlined in red (not for delivery).

## Files

```
out/rally_inwallet_2160x1440_{a,b}.png   master @2x
out/rally_inwallet_1080x720_{a,b}.png    delivery, PNG 150 dpi
out/rally_inwallet_1080x720_{a,b}.jpg    delivery, JPG q92 150 dpi
out/rally_inwallet_720x720_{a,b}.png     square list-card thumbnail
out/proof_safezone_a.png                 safe-zone proof
out/preview_sheet.png                    A/B comparison sheet
```

**Variant A** — reward-first: `GET 400 / RALLY POINTS` · *Connect with MetaMask · New Rally users* · **Join Rally**
**Variant B** — action-first: `CONNECT WITH / METAMASK` · *New Rally users get 400 Rally Points* · **Join Rally**

Variant A is the recommended one: the number is the offer, and the benefit list card shows
the image before anyone reads the description.

## Brand assets used

| Asset | Source |
| --- | --- |
| `assets/rally_logo_blanco.svg` → `.png` | official white Rally lockup (iso + wordmark), from the Rally brand folder in Drive |
| `assets/paloma03.png` | `paloma volando 03` — the mail-pigeon mascot |
| Palette | rally.fun/brand: Dark violet `#25043A`, Rally Violet `#6D37D5`, Light violet `#E5D6FF`, Orange `#FF4E00` |

The logo PNG is rendered from the SVG with headless Chromium at 2880 px wide, so it stays
crisp at any banner size; re-render with:

```bash
chromium --headless --default-background-color=00000000 --window-size=2880,688 \
  --screenshot=assets/rally_logo_blanco.png assets/_wrap.html
```

Headline and sub type is **Archivo Condensed Black Italic / Archivo SemiBold** (SIL OFL) —
an open-source stand-in that matches the logo's heavy italic. Swap `DISPLAY` / `UI` in
`make_banner.py` for Rally's licensed brand font when it turns up; there is no font file in
the Drive folders.

MetaMask is referenced by name only. Their fox mark is not used — using it needs the asset
and sign-off from MetaMask.

## Copy deck (Benefit Simulator fields)

| Field | Value |
| --- | --- |
| **Title** (44/50) | `Connect with MetaMask. Get 400 Rally Points.` |
| | alt: `Get 400 Rally Points on Rally` (29) |
| **CTA Button Text** | `Join Rally` — matches the button in the image |
| **Action URL** | `https://app.rally.fun` |
| **Category** | `Earn Rewards` |
| **Provider Name** | `Rally` |
| **Image** | `out/rally_inwallet_1080x720_a.png` |

### Description

First line is the short description shown in the list card (65/70). Full text is 615/700.

```
Rally is now live on MetaMask Rewards — 400 points for new users.

Rally is featured inside MetaMask Rewards for one week. New Rally users who connect with MetaMask get 400 Rally Points.

VALUE: 400 Rally Points.

ELIGIBILITY: New Rally users connecting with MetaMask. If you don't qualify: existing Rally accounts won't receive the points.

STEPS:
1. Open Rally from MetaMask Rewards, or go to app.rally.fun
2. Connect with MetaMask
3. Your Rally account is created and the points are credited

NEXT: Your 400 Rally Points appear in your Rally account once the MetaMask connection completes.

See you at the Rally.
```

**To confirm before submitting**: the exact crediting timing (the brief says "just by
connecting", the NEXT line assumes it is immediate), the campaign start/end dates, and
whether the Benefit Simulator's MetaMask tab uses the same title/description limits as the
Solflare tab those numbers came from.

## Regenerating

```bash
./fetch_fonts.sh          # Archivo + Inter (SIL OFL) — already vendored in fonts/
pip install Pillow
python3 make_banner.py    # writes every deliverable into out/
```

Copy lives in the `VARIANTS` dict at the top of `make_banner.py`; every headline line
auto-shrinks to stay inside the safe zone, so new copy can be dropped straight in.
