// Rally · Permissionless Campaigns — FULL CAMPAIGN KIT (Rally comic style)
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

function zigzag(w, h, dark = false) {
  const base = dark ? "#20092C" : PLUM, tone = dark ? "#180620" : PLUM_D;
  return `<defs><pattern id="zz" width="360" height="300" patternUnits="userSpaceOnUse" patternTransform="rotate(-10)">
      <rect width="360" height="300" fill="${base}"/>
      <path d="M0,80 L90,20 L180,80 L270,20 L360,80 L360,170 L270,110 L180,170 L90,110 L0,170 Z" fill="${tone}"/>
      <path d="M0,230 L90,170 L180,230 L270,170 L360,230 L360,300 L0,300 Z" fill="${tone}" fill-opacity="0.55"/>
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
function pill(x, y, w, h, fillC, label, labelC, value = "", valueC = ORANGE, fs = 30) {
  return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${h / 2}" fill="${fillC}"/>
    <text x="${x + 34}" y="${y + h / 2 + fs * 0.36}" ${FB} font-size="${fs}" fill="${labelC}">${esc(label)}</text>
    ${value ? `<text x="${x + w - 34}" y="${y + h / 2 + fs * 0.45}" ${FB} font-size="${fs * 1.4}" fill="${valueC}" text-anchor="end">${esc(value)}</text>` : ""}`;
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
const wing = async (file, size, rot = 0) => {
  let s = sharp(B(file)).resize(size);
  if (rot) s = s.rotate(rot, { background: { r: 0, g: 0, b: 0, alpha: 0 } });
  return s.png().toBuffer();
};
const silhouette = async (file, size, rgb = [16, 5, 24], rot = 0) => {
  let s = sharp(B(file)).resize(size).linear([0, 0, 0], rgb);
  if (rot) s = s.rotate(rot, { background: { r: 0, g: 0, b: 0, alpha: 0 } });
  return s.png().toBuffer();
};

(async () => {
  const W = 1600, H = 900, M = 90;

  // ════ A · TEASER — "Something permissionless is coming" ═════════════════
  {
    const svg = `${zigzag(W, H, true)}`;
    const overlay = `
    ${badge(M, 150, "PRE-LAUNCH", PURPLE, WHITE, 28)}
    ${display(M, 360, "SOMETHING", 128, WHITE, 5, -4)}
    ${display(M, 500, "PERMISSIONLESS", 128, ORANGE, 5, -4)}
    ${display(M, 640, "IS COMING.", 128, WHITE, 5, -4)}
    <text x="${M}" y="${H - 70}" ${FB} font-size="30" fill="${LAV}" fill-opacity="0.7">AUG 17 · app.rally.fun</text>
    ${eggMark(1462, 64, 100, WHITE, "#20092C")}`;
    const sil = await silhouette("wingston5.png", 700, [58, 32, 82], -8);
    await compose("teaser_coming_1600x900.png", W, H, svg, [{ input: sil, left: 950, top: 380 }], overlay);
  }

  // ════ B · COUNTDOWN ×3 ══════════════════════════════════════════════════
  for (const d of [3, 2, 1]) {
    const svg = `${zigzag(W, H)}
    ${badge(M, 150, "PRE-LAUNCH", PURPLE, WHITE, 28)}
    ${display(M, 400, "THE CAMPAIGN", 108, WHITE, 4, -4)}
    ${display(M, 520, "BUTTON BELONGS", 108, WHITE, 4, -4)}
    ${display(M, 640, "TO EVERYONE.", 108, ORANGE, 4, -4)}
    <circle cx="1300" cy="470" r="170" fill="${ORANGE}"/>
    <circle cx="1300" cy="470" r="196" fill="none" stroke="${PURPLE}" stroke-width="7" stroke-dasharray="6 26" stroke-linecap="round"/>
    <g transform="translate(1300 545) skewX(-4)"><text x="0" y="0" ${FB} font-size="230" fill="${WHITE}" text-anchor="middle">${d}</text></g>
    <g transform="translate(1300 700) skewX(-6)"><text x="0" y="0" ${FB} font-size="44" fill="${LAV}" text-anchor="middle" letter-spacing="6">${d === 1 ? "DAY" : "DAYS"}</text></g>
    <text x="${M}" y="${H - 70}" ${FB} font-size="30" fill="${LAV}" fill-opacity="0.7">app.rally.fun</text>
    ${eggMark(1462, 64, 100)}`;
    await compose(`countdown_rally_${d}days_1600x900.png`, W, H, svg);
  }

  // ════ C · LAUNCH OG — No sales call / agency / permission ═══════════════
  {
    const svg = `${zigzag(W, H)}`;
    const overlay = `
    ${badge(M, 150, "LIVE NOW", ORANGE, WHITE, 28)}
    ${display(M, 350, "NO SALES CALL.", 120, WHITE, 5, -4)}
    ${display(M, 483, "NO AGENCY.", 120, WHITE, 5, -4)}
    ${display(M, 616, "NO PERMISSION.", 120, ORANGE, 5, -4)}
    ${pill(M, 690, 780, 76, PURPLE, "Permissionless Campaigns", WHITE, "LIVE", WHITE, 32)}
    <text x="${M}" y="${H - 46}" ${FB} font-size="30" fill="${LAV}" fill-opacity="0.8">app.rally.fun</text>
    ${eggMark(1462, 64, 100)}`;
    const w5 = await wing("wingston5.png", 480, -8);
    await compose("launch_og_rally_1600x900.png", W, H, svg, [{ input: w5, left: 1130, top: 470 }], overlay);
  }

  // ════ D · HOW IT WORKS — minutes not meetings ═══════════════════════════
  {
    const steps = ["WRITE", "FUND", "ESCROW", "LAUNCH"];
    let flow = "";
    steps.forEach((st, i) => {
      const x = M + 40 + i * 350;
      flow += `<g transform="translate(${x} 640) skewX(-6)">
        <rect x="-20" y="-52" width="280" height="104" rx="20" fill="${i === 3 ? ORANGE : INKP}" stroke="${i === 3 ? ORANGE : PURPLE}" stroke-width="5"/>
        <text x="120" y="-62" ${FB} font-size="30" fill="${i === 3 ? ORANGE : PURPLE}" text-anchor="middle">0${i + 1}</text>
        <text x="120" y="16" ${FB} font-size="44" fill="${WHITE}" text-anchor="middle" letter-spacing="1">${st}</text></g>
      ${i < 3 ? `<text x="${x + 285}" y="655" ${FB} font-size="46" fill="${ORANGE}">→</text>` : ""}`;
    });
    const svg = `${zigzag(W, H)}
    ${badge(M, 150, "HOW IT WORKS", PURPLE, WHITE, 28)}
    ${display(M, 360, "MINUTES,", 150, WHITE, 6, -4)}
    ${display(M, 520, "NOT MEETINGS.", 150, ORANGE, 6, -4)}
    ${flow}
    <text x="${M}" y="${H - 60}" ${FB} font-size="28" fill="${LAV}" fill-opacity="0.85">Validators score every entry · winners paid automatically · app.rally.fun</text>
    ${eggMark(1462, 64, 100)}`;
    await compose("howitworks_og_rally_1600x900.png", W, H, svg);
  }

  // ════ E · VERIFIED ONE-PAGER (1080×1350 vertical) ══════════════════════
  {
    const w = 1080, h = 1350, m = 70;
    const svg = `${zigzag(w, h)}`;
    const overlay = `
    ${badge(m, 120, "FOR PROJECTS LAUNCHING SOON", ORANGE, WHITE, 26)}
    ${display(m, 260, "VERIFIED", 130, WHITE, 5, -4)}
    ${display(m, 375, "CAMPAIGNS", 130, WHITE, 5, -4)}
    <text x="${m + 4}" y="430" ${FB} font-size="34" fill="${ORANGE}" letter-spacing="2">THE MAIN STAGE OF RALLY</text>

    <g transform="translate(${w - 320} 150)"><rect width="250" height="76" rx="38" fill="${INKP}" stroke="${ORANGE}" stroke-width="5"/>
      <text x="125" y="52" ${FB} font-size="42" fill="${ORANGE}" text-anchor="middle">$1,500</text></g>

    ${pill(m, 480, 940, 92, LAV, "① Priority positioning", INKP, "+ BADGE", ORANGE_D, 34)}
    ${pill(m, 592, 940, 92, PURPLE, "② Your own Community", WHITE, "IN RALLY", WHITE, 34)}
    ${pill(m, 704, 940, 92, LAV, "③ Ambassador Program", INKP, "EXCLUSIVE", PURPLE, 34)}
    ${pill(m, 816, 940, 92, PURPLE, "④ Rally marketing pack", WHITE, "ELITE", WHITE, 34)}

    <rect x="${m}" y="960" width="940" height="150" rx="24" fill="${INKP}" stroke="${PURPLE}" stroke-width="5"/>
    <text x="${m + 36}" y="1022" ${FB} font-size="32" fill="${WHITE}">Access to Rally is free. Always.</text>
    <text x="${m + 36}" y="1068" ${FB} font-size="32" fill="${LAV}">Verified buys positioning — the lights, the crowd.</text>

    <g transform="translate(${m} 1160) skewX(-6)"><rect width="560" height="92" rx="18" fill="${ORANGE}"/>
      <text x="280" y="60" ${FB} font-size="40" fill="${WHITE}" text-anchor="middle">BOOK YOUR CALL →</text></g>
    <text x="${m + 4}" y="1310" ${FB} font-size="28" fill="${LAV}" fill-opacity="0.8">app.rally.fun · one call · one week to launch</text>
    ${eggMark(950, 1240, 96)}`;
    const w5 = await wing("wingston5.png", 360, -8);
    await compose("verified_onepager_1080x1350.png", w, h, svg, [{ input: w5, left: 700, top: 240 }], overlay);
  }

  // ════ F · CALL FOR PROJECTS ═════════════════════════════════════════════
  {
    const svg = `${zigzag(W, H)}`;
    const overlay = `
    ${badge(M, 150, "FIRST COHORT · SEPT-OCT LAUNCHES", PURPLE, WHITE, 28)}
    ${display(M, 360, "LAUNCHING", 150, WHITE, 6, -4)}
    ${display(M, 520, "SOON?", 150, ORANGE, 6, -4)}
    <text x="${M}" y="600" ${FB} font-size="36" fill="${LAV}">Run your launch as a Rally campaign.</text>
    ${pill(M, 650, 620, 70, LAV, "Hundreds of creators", INKP, "", ORANGE, 28)}
    ${pill(M, 736, 620, 70, PURPLE, "AI-verified quality", WHITE, "", ORANGE, 28)}
    <g transform="translate(${M + 660} 650)"><rect width="460" height="156" rx="24" fill="${ORANGE}"/>
      <text x="230" y="66" ${FB} font-size="40" fill="${WHITE}" text-anchor="middle">JOIN THE</text>
      <text x="230" y="118" ${FB} font-size="40" fill="${WHITE}" text-anchor="middle">FIRST COHORT →</text></g>
    <text x="${M}" y="${H - 46}" ${FB} font-size="30" fill="${LAV}" fill-opacity="0.8">Pay only for results · app.rally.fun</text>
    ${eggMark(1462, 64, 100)}`;
    const w5 = await wing("wingston5.png", 430, -6);
    await compose("call_for_projects_1600x900.png", W, H, svg, [{ input: w5, left: 1180, top: 120 }], overlay);
  }

  // ════ G · X SPACE COVER — LIVE DEMO ═════════════════════════════════════
  {
    const svg = `${zigzag(W, H)}
    ${badge(M, 150, "X SPACE · THU AUG 20", ORANGE, WHITE, 28)}
    ${display(M, 355, "LAUNCH A CAMPAIGN", 116, WHITE, 5, -4)}
    ${display(M, 486, "IN 10 MINUTES.", 116, ORANGE, 5, -4)}
    ${pill(M, 560, 700, 76, PURPLE, "Live build, on stream", WHITE, "REAL $", WHITE, 30)}
    <text x="${M}" y="710" ${FB} font-size="32" fill="${LAV}">The campaign we create is the takeaway — join it live.</text>
    <g transform="translate(1310 620)">
      <circle r="130" fill="${INKP}" stroke="${PURPLE}" stroke-width="7"/>
      <rect x="-34" y="-74" width="68" height="104" rx="34" fill="${LAV}"/>
      <path d="M-58,-6 a58,58 0 0 0 116,0" fill="none" stroke="${LAV}" stroke-width="14" stroke-linecap="round"/>
      <line x1="0" y1="56" x2="0" y2="86" stroke="${LAV}" stroke-width="14" stroke-linecap="round"/>
    </g>
    <text x="${M}" y="${H - 46}" ${FB} font-size="30" fill="${LAV}" fill-opacity="0.8">app.rally.fun</text>
    ${eggMark(1462, 64, 100)}`;
    await compose("space_livedemo_1600x900.png", W, H, svg);
  }

  // ════ H · X SPACE COVER — CREATORS & PARTNERS AMA ═══════════════════════
  {
    const svg = `${zigzag(W, H)}`;
    const overlay = `
    ${badge(M, 150, "X SPACE · SAT AUG 22", PURPLE, WHITE, 28)}
    ${display(M, 360, "CREATORS &", 140, WHITE, 6, -4)}
    ${display(M, 510, "PARTNERS AMA", 140, ORANGE, 6, -4)}
    <text x="${M}" y="595" ${FB} font-size="36" fill="${LAV}">First campaigns debrief — the people who launched, on stage.</text>
    ${pill(M, 650, 760, 76, PURPLE, "First numbers of the week", WHITE, "LIVE", WHITE, 30)}
    <text x="${M}" y="${H - 46}" ${FB} font-size="30" fill="${LAV}" fill-opacity="0.8">app.rally.fun</text>
    ${eggMark(1462, 64, 100)}`;
    const w1 = await wing("wingston1.png", 520);
    await compose("space_ama_1600x900.png", W, H, svg, [{ input: w1, left: 1140, top: 500 }], overlay);
  }

  // ════ I · SPOTLIGHT TEMPLATE — best campaigns of the week ═══════════════
  {
    let slots = "";
    for (let i = 0; i < 3; i++) {
      const x = M + i * 490;
      slots += `
      <rect x="${x}" y="400" width="440" height="380" rx="24" fill="${INKP}" fill-opacity="0.8" stroke="${PURPLE}" stroke-width="5" stroke-dasharray="16 14"/>
      ${badge(x + 14, 392, `TOP ${i + 1}`, i === 0 ? ORANGE : PURPLE, WHITE, 30)}
      <text x="${x + 220}" y="590" ${FB} font-size="30" fill="${LAV}" fill-opacity="0.45" text-anchor="middle">[ CAMPAIGN</text>
      <text x="${x + 220}" y="630" ${FB} font-size="30" fill="${LAV}" fill-opacity="0.45" text-anchor="middle">SCREENSHOT ]</text>
      ${pill(x + 24, 700, 392, 58, i === 0 ? ORANGE : PURPLE, "@launcher", WHITE, "$POOL", WHITE, 24)}`;
    }
    const svg = `${zigzag(W, H)}
    ${badge(M, 140, "EVERY MONDAY", ORANGE, WHITE, 28)}
    ${display(M, 262, "BEST CAMPAIGNS", 104, WHITE, 5, -4)}
    ${display(M, 338, "OF THE WEEK", 58, ORANGE, 3, -4)}
    ${slots}
    <text x="${M}" y="${H - 40}" ${FB} font-size="30" fill="${LAV}" fill-opacity="0.85">Your idea is a campaign. Next Monday you could be on this list → app.rally.fun</text>
    ${eggMark(1462, 60, 96)}`;
    await compose("spotlight_template_1600x900.png", W, H, svg);
  }

  // ════ J · CASE STUDY NUMBERS TEMPLATE ═══════════════════════════════════
  {
    const stats = [["XX", "CAMPAIGNS", "LAUNCHED"], ["$X,XXX", "IN REWARDS", "PAID OUT"], ["XXX", "CREATORS", "COMPETING"]];
    let statSvg = "";
    stats.forEach(([n, l1, l2], i) => {
      const x = M + i * 490;
      statSvg += `
      <rect x="${x}" y="420" width="440" height="330" rx="24" fill="${INKP}" fill-opacity="0.85" stroke="${i === 1 ? ORANGE : PURPLE}" stroke-width="6"/>
      <g transform="translate(${x + 220} 570) skewX(-4)"><text ${FB} font-size="100" fill="${i === 1 ? ORANGE : WHITE}" text-anchor="middle">${n}</text></g>
      <text x="${x + 220}" y="650" ${FB} font-size="34" fill="${LAV}" text-anchor="middle">${l1}</text>
      <text x="${x + 220}" y="695" ${FB} font-size="34" fill="${LAV}" text-anchor="middle">${l2}</text>`;
    });
    const svg = `${zigzag(W, H)}
    ${badge(M, 140, "10 DAYS AFTER THE VIDEO", PURPLE, WHITE, 28)}
    ${display(M, 330, "THE RECEIPTS.", 150, WHITE, 6, -4)}
    ${statSvg}
    <g transform="translate(${M} ${H - 90}) skewX(-6)"><rect width="620" height="70" rx="14" fill="${ORANGE}"/>
      <text x="310" y="47" ${FB} font-size="34" fill="${WHITE}" text-anchor="middle">THIS COULD BE YOUR LAUNCH →</text></g>
    <text x="${M + 660}" y="${H - 44}" ${FB} font-size="28" fill="${LAV}" fill-opacity="0.8">app.rally.fun</text>
    ${eggMark(1462, 60, 96)}`;
    await compose("casestudy_numbers_template_1600x900.png", W, H, svg);
  }

  // ════ K · CAMPAIGN IDEA BATTLE (1080×1080) ══════════════════════════════
  {
    const w = 1080, h = 1080, m = 64;
    let bracket = "";
    const slotY = [300, 420, 620, 740];
    slotY.forEach((y, i) => {
      bracket += `<rect x="${m}" y="${y}" width="380" height="86" rx="18" fill="${INKP}" stroke="${PURPLE}" stroke-width="4"/>
      <text x="${m + 28}" y="${y + 54}" ${FB} font-size="30" fill="${LAV}" fill-opacity="0.6">IDEA ${i + 1}</text>`;
    });
    bracket += `
    <path d="M${m + 380},343 h40 v120 h-40 M${m + 380},663 h40 v120 h-40" stroke="${PURPLE}" stroke-width="5" fill="none"/>
    <rect x="${m + 440}" y="380" width="300" height="86" rx="18" fill="${INKP}" stroke="${ORANGE}" stroke-width="4"/>
    <rect x="${m + 440}" y="660" width="300" height="86" rx="18" fill="${INKP}" stroke="${ORANGE}" stroke-width="4"/>
    <path d="M${m + 740},423 h36 v280 h-36" stroke="${ORANGE}" stroke-width="5" fill="none"/>
    <g transform="translate(${m + 790} 500)"><rect width="180" height="130" rx="20" fill="${ORANGE}"/>
      <text x="90" y="55" ${FB} font-size="30" fill="${WHITE}" text-anchor="middle">WINNER</text>
      <text x="90" y="100" ${FB} font-size="36" fill="${WHITE}" text-anchor="middle">FUNDED</text></g>`;
    const svg = `${zigzag(w, h)}
    ${badge(m, 110, "COMMUNITY DAY · SAT AUG 29", ORANGE, WHITE, 26)}
    ${display(m, 210, "CAMPAIGN IDEA", 86, WHITE, 4, -4)}
    ${display(m, 302, "BATTLE", 120, ORANGE, 5, -4)}
    <g transform="translate(0 60)">${bracket}</g>
    <text x="${m}" y="${h - 90}" ${FB} font-size="32" fill="${WHITE}">The winning idea gets funded. For real.</text>
    <text x="${m}" y="${h - 44}" ${FB} font-size="28" fill="${LAV}" fill-opacity="0.8">Drop your idea in the replies → app.rally.fun</text>
    ${eggMark(950, 940, 100)}`;
    await compose("idea_battle_1080x1080.png", w, h, svg);
  }

  // ════ L · EMAIL HEADER (1200×400) ═══════════════════════════════════════
  {
    const w = 1200, h = 400;
    const logoW = fs.readFileSync(B("rally_white.png")).toString("base64");
    const svg = `${zigzag(w, h)}
    <image x="80" y="70" width="300" height="72" href="data:image/png;base64,${logoW}"/>
    ${display(84, 250, "THE NEXT EVOLUTION", 62, WHITE, 2, -4)}
    ${display(84, 320, "OF RALLY.", 62, ORANGE, 2, -4)}
    ${badge(850, 130, "AUG 17", ORANGE, WHITE, 26)}
    <text x="84" y="366" ${FB} font-size="22" fill="${LAV}" fill-opacity="0.7">PERMISSIONLESS CAMPAIGNS</text>
    ${eggMark(1080, 240, 96)}`;
    await compose("email_header_rally_1200x400.png", w, h, svg);
  }
})();
