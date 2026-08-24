// Rally · Pricing — Network vs Verified (Rally comic style)
const sharp = require("sharp");
const fs = require("fs");
const path = require("path");

const OUT = path.join(__dirname, "designs");
const B = (n) => path.join(__dirname, "brand", n);

const PLUM = "#2A1038", PLUM_D = "#20092C", INKP = "#1C0827";
const ORANGE = "#FF4E00", ORANGE_D = "#E8440A";
const PURPLE = "#8B5CF6", LAV = "#C9B8F0";
const WHITE = "#FFFFFF";
const FB = `font-family="Outfit" font-weight="bold"`;
const esc = (t) => t.replace(/&/g, "&amp;").replace(/</g, "&lt;");

function zigzag(w, h) {
  return `<defs><pattern id="zz" width="360" height="300" patternUnits="userSpaceOnUse" patternTransform="rotate(-10)">
      <rect width="360" height="300" fill="${PLUM}"/>
      <path d="M0,80 L90,20 L180,80 L270,20 L360,80 L360,170 L270,110 L180,170 L90,110 L0,170 Z" fill="${PLUM_D}"/>
      <path d="M0,230 L90,170 L180,230 L270,170 L360,230 L360,300 L0,300 Z" fill="${PLUM_D}" fill-opacity="0.55"/>
    </pattern></defs>
    <rect x="-80" y="-80" width="${w + 160}" height="${h + 160}" fill="url(#zz)"/>`;
}
function display(x, y, text, size, fill, stroke = 0, skew = -5, anchor = "start", ls = "-2") {
  const st = stroke ? `stroke="${fill}" stroke-width="${stroke}" stroke-linejoin="round"` : "";
  return `<g transform="translate(${x} ${y}) skewX(${skew})">
    <text x="0" y="0" ${FB} font-size="${size}" fill="${fill}" ${st} text-anchor="${anchor}" letter-spacing="${ls}">${esc(text)}</text></g>`;
}
function badge(x, y, text, fillC = PURPLE, textC = WHITE, size = 34, padX = 22) {
  const w = text.length * size * 0.62 + padX * 2;
  return `<g transform="translate(${x} ${y}) skewX(-8)">
    <rect x="0" y="${-size - 12}" width="${w}" height="${size + 24}" rx="6" fill="${fillC}"/>
    <text x="${padX}" y="0" ${FB} font-size="${size}" fill="${textC}">${esc(text)}</text></g>`;
}
function eggMark(x, y, s, eggC = WHITE, boltC = PLUM) {
  return `<g transform="translate(${x} ${y}) scale(${s / 100}) rotate(8)">
    <path d="M50,4 C70,4 85,28 85,56 C85,80 70,96 50,96 C30,96 15,80 15,56 C15,28 30,4 50,4 Z" fill="${eggC}"/>
    <path d="M56,14 L36,52 L48,52 L40,86 L66,44 L52,44 Z" fill="${boltC}"/></g>`;
}
async function compose(name, w, h, svg, layers = [], overlay = "") {
  const base = await sharp(Buffer.from(`<svg width="${w}" height="${h}" xmlns="http://www.w3.org/2000/svg">${svg}</svg>`)).png().toBuffer();
  const all = [...layers];
  if (overlay) all.push({ input: await sharp(Buffer.from(`<svg width="${w}" height="${h}" xmlns="http://www.w3.org/2000/svg">${overlay}</svg>`)).png().toBuffer(), left: 0, top: 0 });
  let img = sharp(base);
  if (all.length) img = img.composite(all);
  await img.png().toFile(path.join(OUT, name));
  console.log("✓", name);
}

// feature row: label left, value right, inside a rounded pill
function row(x, y, w, label, value, valueC, opts = {}) {
  const h = 58, fs = 24, dim = opts.dim, star = opts.star;
  const bg = star ? PLUM_D : "#241031";
  const strokeC = star ? ORANGE : "#3A1C4E";
  return `
  <rect x="${x}" y="${y}" width="${w}" height="${h}" rx="14" fill="${bg}" stroke="${strokeC}" stroke-width="${star ? 5 : 3}"/>
  <text x="${x + 26}" y="${y + h / 2 + 9}" ${FB} font-size="${fs}" fill="${LAV}" fill-opacity="${dim ? 0.55 : 0.9}">${esc(label)}</text>
  <text x="${x + w - 26}" y="${y + h / 2 + 10}" ${FB} font-size="${fs * 1.25}" fill="${valueC}" fill-opacity="${dim ? 0.6 : 1}" text-anchor="end">${esc(value)}</text>`;
}

(async () => {
  const W = 1920, H = 1080;
  const cardY = 272, cardH = 736, cardW = 836;
  const x1 = 96, x2 = 988;
  const rowsY = cardY + 186, rowGap = 70, rowW = cardW - 72;

  const svg = `${zigzag(W, H)}
  ${badge(96, 130, "PRICING", PURPLE, WHITE, 30)}
  ${display(96, 240, "PERMISSIONLESS", 100, WHITE, 5, -4)}
  ${display(966, 240, "CAMPAIGNS", 100, ORANGE, 5, -4)}

  <!-- ── NETWORK ─────────────────────────────────────── -->
  <rect x="${x1}" y="${cardY}" width="${cardW}" height="${cardH}" rx="30" fill="${INKP}" fill-opacity="0.9" stroke="${PURPLE}" stroke-width="6"/>
  <g transform="translate(${x1 + cardW - 240} ${cardY - 26})"><rect width="216" height="72" rx="36" fill="${INKP}" stroke="${PURPLE}" stroke-width="5"/>
    <text x="108" y="49" ${FB} font-size="40" fill="${LAV}" text-anchor="middle">FREE</text></g>
  ${display(x1 + 36, cardY + 106, "NETWORK", 78, WHITE, 3, -4)}
  <text x="${x1 + 40}" y="${cardY + 150}" ${FB} font-size="27" fill="${PURPLE}" letter-spacing="2">THE OPEN FLOOR</text>
  ${row(x1 + 36, rowsY + 0 * rowGap, rowW, "Campaigns", "UNLIMITED", LAV)}
  ${row(x1 + 36, rowsY + 1 * rowGap, rowW, "Organizations", "ONLY 1", PURPLE, { star: false })}
  ${row(x1 + 36, rowsY + 2 * rowGap, rowW, "Rewards", "USDC | RLPs", LAV)}
  ${row(x1 + 36, rowsY + 3 * rowGap, rowW, "Visibility", "STANDARD", LAV, { dim: true })}
  ${row(x1 + 36, rowsY + 4 * rowGap, rowW, "Marketing from Rally socials", "—", LAV, { dim: true })}
  ${row(x1 + 36, rowsY + 5 * rowGap, rowW, "Community", "—", LAV, { dim: true })}
  ${row(x1 + 36, rowsY + 6 * rowGap, rowW, "Elite creators", "—", LAV, { dim: true })}
  <text x="${x1 + 40}" y="${cardY + cardH - 26}" ${FB} font-size="25" fill="${LAV}" fill-opacity="0.85">✓  Write it. Fund it. Launch it. No permission.</text>

  <!-- ── VERIFIED ────────────────────────────────────── -->
  <rect x="${x2}" y="${cardY}" width="${cardW}" height="${cardH}" rx="30" fill="${INKP}" fill-opacity="0.92" stroke="${ORANGE}" stroke-width="8"/>
  <g transform="translate(${x2 + cardW - 264} ${cardY - 26})"><rect width="240" height="72" rx="36" fill="${ORANGE}"/>
    <text x="120" y="49" ${FB} font-size="40" fill="${WHITE}" text-anchor="middle">$1,500</text></g>
  ${badge(x2 + 24, cardY + 12, "MAIN STAGE", ORANGE, WHITE, 26)}
  ${display(x2 + 36, cardY + 106, "VERIFIED", 78, WHITE, 3, -4)}
  <text x="${x2 + 40}" y="${cardY + 150}" ${FB} font-size="27" fill="${ORANGE}" letter-spacing="2">EVERYTHING IN NETWORK, PLUS:</text>
  ${row(x2 + 36, rowsY + 0 * rowGap, rowW, "Campaigns", "UNLIMITED", WHITE)}
  ${row(x2 + 36, rowsY + 1 * rowGap, rowW, "Organizations", "UNLIMITED", ORANGE, { star: true })}
  ${row(x2 + 36, rowsY + 2 * rowGap, rowW, "Rewards", "USDC | RLPs | TOKENS", ORANGE)}
  ${row(x2 + 36, rowsY + 3 * rowGap, rowW, "Visibility", "PRIORITY + BADGE", ORANGE)}
  ${row(x2 + 36, rowsY + 4 * rowGap, rowW, "Marketing from Rally socials", "INCLUDED", ORANGE)}
  ${row(x2 + 36, rowsY + 5 * rowGap, rowW, "Community", "YOUR OWN", ORANGE)}
  ${row(x2 + 36, rowsY + 6 * rowGap, rowW, "Elite creators", "UNLOCKED", ORANGE)}
  <text x="${x2 + 40}" y="${cardY + cardH - 26}" ${FB} font-size="25" fill="#FFD9C7" fill-opacity="0.95">✓  Your project on the main stage, from day one.</text>

  <!-- VS chip between cards -->
  <circle cx="960" cy="${cardY + cardH / 2}" r="52" fill="${ORANGE}" stroke="${PLUM_D}" stroke-width="8"/>
  <g transform="translate(960 ${cardY + cardH / 2 + 14}) skewX(-6)"><text x="0" y="0" ${FB} font-size="42" fill="${WHITE}" text-anchor="middle">VS</text></g>

  <text x="96" y="${H - 40}" ${FB} font-size="30" fill="${LAV}" fill-opacity="0.85">Start free on Network · book Verified for your launch → app.rally.fun</text>
  ${eggMark(1770, 56, 100)}`;

  // NEW tag over the Verified orgs row (drawn in overlay so it sits on top)
  const newTagX = x2 + 36 + rowW / 2 - 20, newTagY = rowsY + 1 * rowGap - 20;
  const overlay = `
  <g transform="translate(${newTagX} ${newTagY}) skewX(-8) rotate(-3)">
    <rect x="0" y="0" width="86" height="38" rx="8" fill="${WHITE}"/>
    <text x="43" y="27" ${FB} font-size="24" fill="${ORANGE_D}" text-anchor="middle">NEW</text></g>`;

  const wing = await sharp(B("wingston5.png")).resize(400).rotate(-8, { background: { r: 0, g: 0, b: 0, alpha: 0 } }).png().toBuffer();
  await compose("pricing_network_vs_verified_1920x1080.png", W, H, svg, [
    { input: wing, left: 1510, top: 840 },
  ], overlay);
})();
