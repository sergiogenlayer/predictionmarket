// Rally · Permissionless Campaigns — batch 2 · REAL Rally comic style
// deep plum + zigzag, chunky skewed type, purple/orange cards, Wingston NFT art
const sharp = require("sharp");
const fs = require("fs");
const path = require("path");

const OUT = path.join(__dirname, "designs");
const B = (n) => path.join(__dirname, "brand", n);

// palette sampled from official posters
const PLUM = "#2A1038", PLUM_D = "#20092C", INKP = "#1C0827";
const ORANGE = "#FF4E00", ORANGE_D = "#E8440A";
const PURPLE = "#8B5CF6", LAV = "#C9B8F0", LAV_D = "#B9A5E8";
const WHITE = "#FFFFFF";
const FB = `font-family="Outfit" font-weight="bold"`;

const esc = (t) => t.replace(/&/g, "&amp;").replace(/</g, "&lt;");

// tonal zigzag field (the brand background)
function zigzag(w, h) {
  return `<defs><pattern id="zz" width="360" height="300" patternUnits="userSpaceOnUse" patternTransform="rotate(-10)">
      <rect width="360" height="300" fill="${PLUM}"/>
      <path d="M0,80 L90,20 L180,80 L270,20 L360,80 L360,170 L270,110 L180,170 L90,110 L0,170 Z" fill="${PLUM_D}"/>
      <path d="M0,230 L90,170 L180,230 L270,170 L360,230 L360,300 L0,300 Z" fill="${PLUM_D}" fill-opacity="0.55"/>
    </pattern></defs>
    <rect x="-80" y="-80" width="${w + 160}" height="${h + 160}" fill="url(#zz)"/>`;
}

// chunky display text: bold + stroke + skew
function display(x, y, text, size, fill, stroke = 0, skew = -5, anchor = "start", ls = "-2") {
  const st = stroke ? `stroke="${fill}" stroke-width="${stroke}" stroke-linejoin="round"` : "";
  return `<g transform="translate(${x} ${y}) skewX(${skew})">
    <text x="0" y="0" ${FB} font-size="${size}" fill="${fill}" ${st} text-anchor="${anchor}" letter-spacing="${ls}">${esc(text)}</text></g>`;
}

// skewed badge (the "Path 1" style tag)
function badge(x, y, text, fillC = PURPLE, textC = WHITE, size = 34, padX = 22) {
  const w = text.length * size * 0.62 + padX * 2;
  return `<g transform="translate(${x} ${y}) skewX(-8)">
    <rect x="0" y="${-size - 12}" width="${w}" height="${size + 24}" rx="6" fill="${fillC}"/>
    <text x="${padX}" y="0" ${FB} font-size="${size}" fill="${textC}" letter-spacing="0">${esc(text)}</text></g>`;
}

// pill row: label left, value right
function pill(x, y, w, h, fillC, label, labelC, value = "", valueC = ORANGE, fs = 30) {
  return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${h / 2}" fill="${fillC}"/>
    <text x="${x + 34}" y="${y + h / 2 + fs * 0.36}" ${FB} font-size="${fs}" fill="${labelC}">${esc(label)}</text>
    ${value ? `<text x="${x + w - 34}" y="${y + h / 2 + fs * 0.45}" ${FB} font-size="${fs * 1.5}" fill="${valueC}" text-anchor="end">${esc(value)}</text>` : ""}`;
}

// the egg + bolt mark
function eggMark(x, y, s, eggC = WHITE, boltC = PLUM) {
  return `<g transform="translate(${x} ${y}) scale(${s / 100}) rotate(8)">
    <path d="M50,4 C70,4 85,28 85,56 C85,80 70,96 50,96 C30,96 15,80 15,56 C15,28 30,4 50,4 Z" fill="${eggC}"/>
    <path d="M56,14 L36,52 L48,52 L40,86 L66,44 L52,44 Z" fill="${boltC}"/>
  </g>`;
}

async function compose(name, w, h, svg, layers = [], overlay = "") {
  const base = await sharp(Buffer.from(`<svg width="${w}" height="${h}" xmlns="http://www.w3.org/2000/svg">${svg}</svg>`)).png().toBuffer();
  const all = [...layers];
  if (overlay) {
    const ov = await sharp(Buffer.from(`<svg width="${w}" height="${h}" xmlns="http://www.w3.org/2000/svg">${overlay}</svg>`)).png().toBuffer();
    all.push({ input: ov, left: 0, top: 0 });
  }
  let img = sharp(base);
  if (all.length) img = img.composite(all);
  await img.png().toFile(path.join(OUT, name));
  console.log("✓", name);
}

(async () => {
  // ════ 1 · NETWORK vs VERIFIED (1920×1080) ═══════════════════════════════
  {
    const W = 1920, H = 1080;
    const cardY = 400, cardH = 560;
    const svg = `
    ${zigzag(W, H)}
    ${display(96, 165, "TWO WAYS TO LAUNCH A", 54, ORANGE, 0, -8)}
    ${display(90, 330, "CAMPAIGN", 210, WHITE, 6, -4)}
    ${eggMark(1770, 70, 110, WHITE, PLUM)}

    <!-- NETWORK card -->
    <rect x="96" y="${cardY}" width="836" height="${cardH}" rx="30" fill="${INKP}" fill-opacity="0.85" stroke="${PURPLE}" stroke-width="7"/>
    ${badge(120, cardY + 14, "PATH 1", PURPLE)}
    <g transform="translate(${96 + 836 - 250} ${cardY - 24})"><rect width="250" height="70" rx="35" fill="${INKP}" stroke="${PURPLE}" stroke-width="5"/>
      <text x="125" y="48" ${FB} font-size="38" fill="${LAV}" text-anchor="middle">FREE</text></g>
    ${display(132, cardY + 135, "NETWORK", 96, WHITE, 3, -4)}
    <text x="136" y="${cardY + 182}" ${FB} font-size="30" fill="${PURPLE}" letter-spacing="2">THE OPEN FLOOR</text>
    ${pill(132, cardY + 215, 764, 74, LAV, "Anyone can launch", INKP, "NO ORG", PURPLE, 30)}
    ${pill(132, cardY + 305, 764, 74, PURPLE, "Rewards in", WHITE, "USDC | RLPs", WHITE, 30)}
    ${pill(132, cardY + 395, 764, 74, INKP, "From idea to live", LAV, "10 MIN", ORANGE, 30)}
    <text x="136" y="${cardY + 528}" ${FB} font-size="26" fill="${LAV}" fill-opacity="0.85">✓  Write it. Fund it. Launch it. No permission.</text>

    <!-- VERIFIED card -->
    <rect x="988" y="${cardY}" width="836" height="${cardH}" rx="30" fill="${INKP}" fill-opacity="0.85" stroke="${ORANGE}" stroke-width="7"/>
    ${badge(1012, cardY + 14, "PATH 2", ORANGE)}
    <g transform="translate(${988 + 836 - 250} ${cardY - 24})"><rect width="250" height="70" rx="35" fill="${INKP}" stroke="${ORANGE}" stroke-width="5"/>
      <text x="125" y="48" ${FB} font-size="38" fill="${ORANGE}" text-anchor="middle">$1,500</text></g>
    ${display(1024, cardY + 135, "VERIFIED", 96, WHITE, 3, -4)}
    <text x="1028" y="${cardY + 182}" ${FB} font-size="30" fill="${ORANGE}" letter-spacing="2">THE MAIN STAGE</text>
    ${pill(1024, cardY + 215, 764, 74, LAV, "Priority positioning", INKP, "+ BADGE", ORANGE_D, 30)}
    ${pill(1024, cardY + 305, 764, 74, PURPLE, "Your own Community", WHITE, "IN RALLY", WHITE, 30)}
    ${pill(1024, cardY + 395, 764, 74, INKP, "Ambassadors + marketing pack", LAV, "", ORANGE, 30)}
    <text x="1028" y="${cardY + 528}" ${FB} font-size="26" fill="#FFD9C7" fill-opacity="0.95">✓  Access is free. Verified buys the stage.</text>

    <text x="96" y="${H - 40}" ${FB} font-size="30" fill="${WHITE}" fill-opacity="0.85" letter-spacing="1">app.rally.fun</text>
    ${eggMark(60, H - 130, 0.001)}`;
    const wing = await sharp(B("wingston5.png")).resize(430).rotate(-8, { background: { r: 0, g: 0, b: 0, alpha: 0 } }).png().toBuffer();
    await compose("network_vs_verified_1920x1080.png", W, H, svg, [
      { input: wing, left: 1478, top: 812 },
    ]);
  }

  // ════ 2 · WHY PERMISSIONLESS (1920×1080, utilities style) ═══════════════
  {
    const W = 1920, H = 1080;
    const cards = [
      { n: "#1", title: "NO", title2: "GATEKEEPERS", sub: "Write it. Fund it. Launch it.", sub2: "No approval queue." },
      { n: "#2", title: "AI VALIDATORS", title2: "PICK WINNERS", sub: "GPT · Claude · Grok reach", sub2: "consensus onchain." },
      { n: "#3", title: "PAY ONLY", title2: "FOR RESULTS", sub: "Escrow in.", sub2: "Verified results out." },
    ];
    let cardsSvg = "";
    cards.forEach((c, i) => {
      const x = 96 + i * 600, y = 430, w = 540, h = 540;
      cardsSvg += `
      <rect x="${x}" y="${y}" width="${w}" height="${h}" rx="26" fill="${INKP}" fill-opacity="0.88" stroke="${PURPLE}" stroke-width="6"/>
      ${badge(x + 16, y + 10, c.n, PURPLE, WHITE, 40)}
      <g>
        <circle cx="${x + w / 2}" cy="${y + 205}" r="108" fill="${PLUM_D}" stroke="${i === 1 ? ORANGE : PURPLE}" stroke-width="6"/>
        ${i === 0 ? `<g transform="translate(${x + w / 2} ${y + 205})">
            <rect x="-44" y="-14" width="88" height="66" rx="12" fill="${LAV}"/>
            <path d="M-26,-14 v-18 a26,26 0 0 1 52,0 v6" fill="none" stroke="${LAV}" stroke-width="14" stroke-linecap="round"/>
            <line x1="-62" y1="52" x2="62" y2="-52" stroke="${ORANGE}" stroke-width="16" stroke-linecap="round"/>
          </g>`
        : i === 1 ? `<g transform="translate(${x + w / 2} ${y + 205})">
            <circle cx="0" cy="0" r="64" fill="${ORANGE}"/>
            <path d="M10,-46 L-22,8 L-2,8 L-12,46 L26,-8 L6,-8 Z" fill="${WHITE}"/>
            <circle cx="0" cy="0" r="84" fill="none" stroke="${LAV}" stroke-width="6" stroke-dasharray="4 18" stroke-linecap="round"/>
          </g>`
        : `<g transform="translate(${x + w / 2} ${y + 205})">
            <ellipse cx="0" cy="30" rx="64" ry="20" fill="${PURPLE}"/>
            <ellipse cx="0" cy="12" rx="64" ry="20" fill="${LAV}"/>
            <ellipse cx="0" cy="-6" rx="64" ry="20" fill="${PURPLE}"/>
            <ellipse cx="0" cy="-24" rx="64" ry="20" fill="${LAV}"/>
            <ellipse cx="0" cy="-42" rx="64" ry="20" fill="${WHITE}"/>
            <path d="M6,-62 L-12,-34 L-2,-34 L-8,-12 L14,-42 L4,-42 Z" fill="${ORANGE}"/>
          </g>`}
      </g>
      ${display(x + 40, y + 395, c.title, 52, WHITE, 2, -4)}
      ${display(x + 40, y + 452, c.title2, 52, WHITE, 2, -4)}
      <text x="${x + 42}" y="${y + 495}" ${FB} font-size="27" fill="${LAV}" fill-opacity="0.9">${esc(c.sub)}</text>
      <text x="${x + 42}" y="${y + 527}" ${FB} font-size="27" fill="${LAV}" fill-opacity="0.9">${esc(c.sub2)}</text>`;
    });
    const svg = `
    ${zigzag(W, H)}
    ${cardsSvg}
    <text x="96" y="${H - 34}" ${FB} font-size="30" fill="${WHITE}" fill-opacity="0.85">app.rally.fun</text>`;
    const overlay = `
    ${display(96, 150, "RALLY CAMPAIGNS", 54, ORANGE, 0, -8)}
    ${display(90, 330, "WHY PERMISSIONLESS", 158, WHITE, 6, -4)}
    ${eggMark(1774, 66, 104, WHITE, PLUM)}`;
    const wing = await sharp(B("wingston1.png")).resize(560).png().toBuffer();
    const wm = await sharp(wing).metadata();
    await compose("why_permissionless_1920x1080.png", W, H, svg, [
      { input: wing, left: 1920 - wm.width + 150, top: -70 },
    ], overlay);
  }

  // ════ 3 · CAMPAIGNS ARE LIVE (1080×1080, mint-is-live style) ════════════
  {
    const W = 1080, H = 1080;
    const svg = `
    <rect width="${W}" height="${H}" fill="#EE5A0E"/>
    <path d="M0,0 L${W},${H * 0.62} L${W},${H * 0.34} L0,-0.28Z" fill="#F97431" fill-opacity="0.55"/>
    <path d="M-100,${H * 0.42} L${W},${H} L${W * 0.5},${H} L-100,${H * 0.62} Z" fill="#F97431" fill-opacity="0.45"/>
    <path d="M0,${H * 0.12} L${W},${H * 0.66} L${W},${H * 0.6} L0,${H * 0.18} Z" fill="#FFFFFF" fill-opacity="0.18"/>
    <!-- comic clouds -->
    <g fill="#FFFFFF" fill-opacity="0.55">
      <ellipse cx="150" cy="110" rx="90" ry="30"/><ellipse cx="230" cy="90" rx="60" ry="24"/>
      <ellipse cx="950" cy="180" rx="80" ry="26"/><ellipse cx="880" cy="200" rx="55" ry="20"/>
      <ellipse cx="180" cy="950" rx="95" ry="30"/><ellipse cx="270" cy="975" rx="60" ry="22"/>
      <ellipse cx="920" cy="900" rx="75" ry="25"/>
    </g>
    <!-- banner bars (behind Wingston) -->
    <g transform="skewX(-6)">
      <rect x="330" y="380" width="700" height="140" fill="${PURPLE}"/>
      <rect x="560" y="520" width="190" height="80" fill="#F4EDE4"/>
      <rect x="560" y="600" width="480" height="140" fill="${LAV}"/>
    </g>`;
    const overlay = `
    <g transform="skewX(-6)">
      <text x="520" y="486" ${FB} font-size="94" fill="${WHITE}" letter-spacing="-2">CAMPAIGNS</text>
      <text x="588" y="580" ${FB} font-size="56" fill="${ORANGE_D}">ARE</text>
      <text x="586" y="716" ${FB} font-size="112" fill="#5B2EBE" letter-spacing="-1">LIVE</text>
    </g>
    ${eggMark(915, 915, 120, WHITE, "#EE5A0E")}
    <text x="72" y="1030" ${FB} font-size="30" fill="${WHITE}" fill-opacity="0.9">app.rally.fun</text>`;
    const wing = await sharp(B("wingston5.png")).resize(600).rotate(-10, { background: { r: 0, g: 0, b: 0, alpha: 0 } }).png().toBuffer();
    await compose("campaigns_are_live_1080x1080.png", W, H, svg, [
      { input: wing, left: -70, top: 330 },
    ], overlay);
  }
})();
