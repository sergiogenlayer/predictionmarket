const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

const ICONS = path.join(__dirname, "icons");
const img = (n) => "image/png;base64," + fs.readFileSync(path.join(ICONS, n)).toString("base64");

const DARK = "25043A", INK = "2A1A38", MUT = "6B6273", TINT = "F8F1EC", WHITE = "WHITE" && "FFFFFF";
// pillar system colors
const P1 = "FF4E00"; // video — Rally orange
const P2 = "25043A"; // sales — Rally violet
const P3 = "C43C00"; // creators — burnt orange
const P4 = "6E5588"; // education — soft violet
const F = "Calibri";
const DOC = "https://docs.google.com/document/d/1O3oPyaVwuSDak84CgE4xqk1jykADMsvYddNdYAzc_vw/edit";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.defineSlideMaster({ title: "LIGHT", background: { color: WHITE } });
pres.defineSlideMaster({ title: "DARK", background: { color: DARK } });

function head(s, kickerText, titleText) {
  s.addText(kickerText.toUpperCase(), { x: 0.55, y: 0.38, w: 9.8, h: 0.3, fontFace: F, fontSize: 11.5, bold: true, color: P1, charSpacing: 3, margin: 0 });
  s.addText(titleText, { x: 0.55, y: 0.68, w: 12.2, h: 0.6, fontFace: F, fontSize: 27, bold: true, color: INK, margin: 0 });
}
function docChip(s, label) {
  s.addShape("roundRect", { x: 10.55, y: 0.4, w: 2.28, h: 0.36, rectRadius: 0.14, fill: { color: P1 } });
  s.addText("MASTER DOC  ▸", { x: 10.55, y: 0.4, w: 2.28, h: 0.36, fontFace: F, fontSize: 10.5, bold: true, color: DARK, align: "center", valign: "middle", margin: 0, hyperlink: { url: DOC, tooltip: label } });
}
function iconCircle(s, x, y, d, iconFile, color) {
  s.addShape("ellipse", { x, y, w: d, h: d, fill: { color } });
  const pad = d * 0.27;
  s.addImage({ data: img(iconFile), x: x + pad, y: y + pad, w: d - 2 * pad, h: d - 2 * pad });
}

// ══ 1 · COVER ═════════════════════════════════════════════════════════════
{
  const s = pres.addSlide({ masterName: "DARK" });
  s.addImage({ path: path.join(__dirname, "brand/rally_white.png"), x: 0.7, y: 0.7, w: 2.72, h: 0.65 });
  s.addShape("ellipse", { x: 9.55, y: 2.15, w: 2.6, h: 2.6, fill: { color: P1 } });
  s.addImage({ data: img("play-d.png"), x: 10.58, y: 3.15, w: 0.62, h: 0.62 });
  s.addText("GO-TO-MARKET · AUG–SEP 2026", { x: 0.7, y: 1.85, w: 8, h: 0.35, fontFace: F, fontSize: 12.5, bold: true, color: P1, charSpacing: 3, margin: 0 });
  s.addText("Permissionless Campaigns", { x: 0.7, y: 2.25, w: 8.4, h: 0.95, fontFace: F, fontSize: 44, bold: true, color: WHITE, margin: 0 });
  s.addText("2-week launch campaign · 4 activation pillars · every piece already written",
    { x: 0.7, y: 3.25, w: 8.2, h: 0.45, fontFace: F, fontSize: 18, color: "E8DCEF", margin: 0 });
  s.addText("“No sales call. No agency. No permission.”", { x: 0.7, y: 4.0, w: 8, h: 0.4, fontFace: F, fontSize: 15, italic: true, color: P1, margin: 0 });
  s.addText("Launch campaign plan  ·  full copy & scripts: Master Doc", { x: 0.7, y: 6.55, w: 9, h: 0.35, fontFace: F, fontSize: 12, color: "B79ACB", margin: 0, hyperlink: { url: DOC } });
}

// ══ 2 · OBJECTIVES ════════════════════════════════════════════════════════
{
  const s = pres.addSlide({ masterName: "LIGHT" });
  head(s, "Why we run this campaign", "Three objectives, one launch");
  docChip(s, "Objectives");
  const objs = [
    ["handshake-w.png", "CLOSE COMMUNITIES & PROJECTS", "Convert the launch into signed demand.",
      ["First Verified cohort filled ($1,500 × N — the revenue line)", "Flagship communities operating inside Rally (co-created campaign)", "Project pipeline worked 1:1 with one-pager + case study"],
      "KPI: Verified calls booked · cohort filled · communities claimed"],
    ["chart-w.png", "ACQUISITION NARRATIVE", "Own one story: marketing without gatekeepers.",
      ["The Demo Video as acquisition engine — promoted at full throttle", "KOLs launching real RLP-funded campaigns: the promotion IS the product", "Every piece repeats the same hook, twice a week, for two weeks"],
      "KPI: video reach · new sign-ups · campaigns created"],
    ["bolt-w.png", "UNIFY THE CONCEPTS", "One frame that connects everything Rally has built.",
      ["RLPs = working capital · Communities = distribution · Campaigns = the market", "Network (open floor) vs Verified (main stage) — one clean mental model", "Ends at the vision: “Rally, the Hub of Communities”"],
      "KPI: RLPs deployed into pools · consistent narrative across ~25 pieces"],
  ];
  objs.forEach(([icon, h, sub, bullets, kpi], i) => {
    const x = 0.55 + i * 4.18;
    s.addShape("roundRect", { x, y: 1.5, w: 3.9, h: 4.6, rectRadius: 0.1, fill: { color: i === 0 ? DARK : TINT } });
    const dark = i === 0;
    iconCircle(s, x + 0.32, 1.82, 0.62, icon, dark ? P1 : P2);
    s.addText(h, { x: x + 0.32, y: 2.6, w: 3.3, h: 0.55, fontFace: F, fontSize: 14.5, bold: true, color: dark ? P1 : P2, margin: 0, lineSpacing: 16 });
    s.addText(sub, { x: x + 0.32, y: 3.18, w: 3.3, h: 0.42, fontFace: F, fontSize: 11.5, italic: true, color: dark ? "E8DCEF" : MUT, margin: 0, lineSpacing: 13 });
    s.addText(bullets.map((t, j) => ({ text: t, options: { bullet: { code: "2022" }, breakLine: j < bullets.length - 1 } })),
      { x: x + 0.32, y: 3.66, w: 3.35, h: 1.7, fontFace: F, fontSize: 10.5, color: dark ? WHITE : INK, margin: 0, paraSpaceAfter: 6, lineSpacing: 12.5 });
    s.addText(kpi, { x: x + 0.32, y: 5.5, w: 3.35, h: 0.5, fontFace: F, fontSize: 9.5, bold: true, color: dark ? "CBB3DC" : P2, margin: 0, lineSpacing: 11.5 });
  });
  s.addText("The campaign is designed so each pillar serves at least one objective — nothing publishes without a job.",
    { x: 0.55, y: 6.45, w: 12.25, h: 0.35, fontFace: F, fontSize: 12.5, italic: true, color: P2, margin: 0 });
}

// ══ 3 · STRATEGY: 4 PILLARS ══════════════════════════════════════════════
{
  const s = pres.addSlide({ masterName: "LIGHT" });
  head(s, "The strategy", "Four activation pillars — everything else supports these");
  docChip(s, "Strategy");
  const cards = [
    [P1, "play-d.png", "1 · THE PERMISSIONLESS VIDEO", "The hero. Everything derives from it.",
      ["Demo Video promoted at full throttle from Day 1", "KOLs launch real permissionless campaigns funded in RLPs", "Teaser · countdown · cutdowns · receipts thread keep it alive"], "§5, 11.5"],
    [P2, "pen-w.png", "2 · SALES NARRATIVE & CO-MARKETING", "Attract communities and projects.",
      ["Verified & Network pitches + use-case articles", "Call for Projects (first cohort) + flagship co-created campaign", "Case study with real ROI → pipeline + “Hub of Communities” vision"], "§6–7, 11"],
    [P3, "video-w.png", "3 · CREATORS CREATING CAMPAIGNS", "Social proof from other voices.",
      ["Creators launch campaigns with their RLPs — and tell it on video", "Weekly Spotlight of the best community campaigns", "Campaign Idea Battle: winning community idea gets funded"], "§9, 11"],
    [P4, "mic-w.png", "4 · CONCEPT EDUCATION", "Lower the barrier to the first campaign.",
      ["“How It Works” · “Why RLPs Matter” · brief-writing guide", "Live demo: a campaign launched in 10 minutes, on stream", "X Space debrief + AMAs — objections answered in public"], "§8, 10, 13"],
  ];
  cards.forEach(([color, icon, title, sub, bullets, ref], i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.55 + col * 6.25, y = 1.5 + row * 2.62;
    s.addShape("roundRect", { x, y, w: 6.05, h: 2.42, rectRadius: 0.1, fill: { color: TINT } });
    s.addShape("ellipse", { x: x + 0.3, y: y + 0.28, w: 0.55, h: 0.55, fill: { color } });
    s.addImage({ data: img(icon === "play-d.png" ? "play-d.png" : icon), x: x + 0.44, y: y + 0.42, w: 0.27, h: 0.27 });
    s.addText(title, { x: x + 1.02, y: y + 0.26, w: 3.9, h: 0.55, fontFace: F, fontSize: 13.5, bold: true, color, margin: 0, lineSpacing: 15 });
    s.addText("Master Doc " + ref + " ▸", { x: x + 4.6, y: y + 0.28, w: 1.3, h: 0.5, fontFace: F, fontSize: 9, bold: true, color: MUT, align: "right", margin: 0, hyperlink: { url: DOC } });
    s.addText(sub, { x: x + 1.02, y: y + 0.76, w: 4.7, h: 0.3, fontFace: F, fontSize: 10.5, italic: true, color: MUT, margin: 0 });
    s.addText(bullets.map((t, j) => ({ text: t, options: { bullet: { code: "2022" }, breakLine: j < bullets.length - 1 } })),
      { x: x + 0.34, y: y + 1.14, w: 5.5, h: 1.2, fontFace: F, fontSize: 10.5, color: INK, margin: 0, paraSpaceAfter: 4, lineSpacing: 12.5 });
  });
}

// ══ 4–7 · ONE SLIDE PER PILLAR ═══════════════════════════════════════════
const pillars = [
  {
    color: P1, icon: "play-d.png", num: "PILLAR 1", name: "The Permissionless Video",
    serves: "Serves: acquisition narrative + concept unification",
    why: [
      "One heavy production, ~25 pieces living off it — maximum leverage per euro",
      "KOLs don't do ad reads: they launch real campaigns funded in RLPs. Their audience watches the product work",
      "The hook carries the whole story: “Every campaign you've seen here was ours. That ends today.”",
    ],
    contents: [
      ["AUG 24", "Teaser 15s — “Something permissionless is coming”"],
      ["AUG 25", "Countdown post — launch date reveal"],
      ["AUG 26", "DEMO VIDEO (100s, script locked) + launch thread pinned + mailing"],
      ["AUG 26→", "KOL activation: real RLP-funded campaigns + coordinated QT push"],
      ["W1–W2", "Cutdowns 15s / 30s — fresh angles keep it circulating"],
      ["SEP 8", "“Anatomy of a Campaign” receipts thread — the video, proven with screenshots"],
    ], ref: "Master Doc §4–5, 11.5",
  },
  {
    color: P2, icon: "pen-w.png", num: "PILLAR 2", name: "Sales Narrative & Co-marketing",
    serves: "Serves: close communities & projects (the revenue line)",
    why: [
      "Two clean offers: Network (open floor, free) vs Verified (main stage, $1,500)",
      "Co-marketing built in: projects launch WITH us — Call for Projects, flagship co-created campaign",
      "Everything doubles as sales material: one-pager, comparison visual, use cases, case study",
    ],
    contents: [
      ["AUG 27", "Verified thread + “Why Verified — 5 Use Cases” + one-pager → pipeline"],
      ["AUG 28", "Network thread + Verified vs Network visual + CALL FOR PROJECTS (first cohort)"],
      ["SEP 1", "Flagship co-created campaign goes live (partner community)"],
      ["W1–W2", "1:1 outreach to Sept–Oct launches — the video is the pitch"],
      ["SEP 4", "Case study “the receipts” + sales article → pipeline"],
      ["SEP 3", "Vision: “Rally, the Hub of Communities” — the story that closes communities"],
    ], ref: "Master Doc §6–7, 11.3–11.4",
  },
  {
    color: P3, icon: "video-w.png", num: "PILLAR 3", name: "Creators Creating Campaigns",
    serves: "Serves: acquisition narrative + social proof",
    why: [
      "The claim only lands when someone who isn't us says it",
      "Creators spend their own RLPs on their own campaigns — the loop, demonstrated",
      "Community content compounds: every spotlight makes the next creator want in",
    ],
    contents: [
      ["SEP 1", "Creator video #1 — “I launched a campaign, here's what happened” (their words)"],
      ["SEP 7", "Spotlight thread: best community campaigns (recurring every Monday)"],
      ["SEP 2", "Partner video #2 — community-lead POV"],
      ["W2", "Poll feeds the Battle: “What would you launch a campaign for?”"],
      ["SEP 5", "Campaign Idea Battle — the winning community idea gets funded for real"],
    ], ref: "Master Doc §9, 11.1–11.2, 11.6",
  },
  {
    color: P4, icon: "mic-w.png", num: "PILLAR 4", name: "Concept Education",
    serves: "Serves: concept unification + lowering the barrier to campaign #1",
    why: [
      "Ten minutes from idea to live — but only if people know how",
      "Education content is evergreen: it keeps converting after the campaign ends",
      "Objections answered in public build trust faster than any ad",
    ],
    contents: [
      ["AUG 26", "Article: “Permissionless Campaigns — How It Works” (evergreen explainer)"],
      ["AUG 28", "Article: “Why RLPs Matter” — points become working capital"],
      ["AUG 31", "Live demo: “Launch a campaign in 10 minutes” + guide “How to Write a Campaign Brief”"],
      ["AUG 29", "X Space: Creators & Partners AMA — first campaigns debrief"],
      ["ALWAYS", "Objections cheat sheet + tagline bank (Spaces, AMAs, replies)"],
    ], ref: "Master Doc §5.4, 7.5, 8, 10, 13",
  },
];

pillars.forEach((p) => {
  const s = pres.addSlide({ masterName: "LIGHT" });
  // left panel
  s.addShape("rect", { x: 0, y: 0, w: 4.1, h: 7.5, fill: { color: DARK } });
  s.addText(p.num, { x: 0.5, y: 0.65, w: 3.2, h: 0.3, fontFace: F, fontSize: 12, bold: true, color: p.color, charSpacing: 3, margin: 0 });
  iconCircle(s, 0.5, 1.1, 0.75, p.icon, p.color);
  s.addText(p.name, { x: 0.5, y: 2.05, w: 3.3, h: 1.0, fontFace: F, fontSize: 24, bold: true, color: WHITE, margin: 0, lineSpacing: 27 });
  s.addText(p.serves, { x: 0.5, y: 3.1, w: 3.3, h: 0.6, fontFace: F, fontSize: 11.5, italic: true, color: p.color === P1 ? "FFB894" : "CBB3DC", margin: 0, lineSpacing: 14 });
  s.addText(p.why.map((t, j) => ({ text: t, options: { bullet: { code: "2022" }, breakLine: j < p.why.length - 1 } })),
    { x: 0.5, y: 3.85, w: 3.3, h: 3.0, fontFace: F, fontSize: 11, color: "E8F2F0", margin: 0, paraSpaceAfter: 9, lineSpacing: 13.5 });

  // right: contents with dates
  s.addText("CONTENTS & TIMING", { x: 4.6, y: 0.5, w: 5.5, h: 0.3, fontFace: F, fontSize: 11.5, bold: true, color: MUT, charSpacing: 3, margin: 0 });
  docChip(s, p.name);
  const n = p.contents.length;
  const dy = Math.min(1.0, 6.1 / n);
  const rowH = Math.min(0.86, dy - 0.1);
  p.contents.forEach(([when, what], i) => {
    const y = 1.0 + i * dy;
    s.addShape("roundRect", { x: 4.6, y, w: 8.2, h: rowH, rectRadius: 0.08, fill: { color: TINT } });
    s.addShape("roundRect", { x: 4.85, y: y + rowH / 2 - 0.17, w: 1.0, h: 0.34, rectRadius: 0.12, fill: { color: p.color } });
    s.addText(when, { x: 4.85, y: y + rowH / 2 - 0.17, w: 1.0, h: 0.34, fontFace: F, fontSize: 9.5, bold: true, color: p.color === P1 ? DARK : WHITE, align: "center", valign: "middle", margin: 0 });
    s.addText(what, { x: 6.0, y: y + 0.06, w: 6.65, h: rowH - 0.1, fontFace: F, fontSize: 12, color: INK, margin: 0, valign: "middle", lineSpacing: 14.5 });
  });
  s.addText(p.ref + "  ▸", { x: 4.6, y: 7.05, w: 8.2, h: 0.3, fontFace: F, fontSize: 10.5, bold: true, color: MUT, margin: 0, hyperlink: { url: DOC } });
});

// ══ 8 · CALENDAR (color-coded by pillar) ═════════════════════════════════
{
  const s = pres.addSlide({ masterName: "LIGHT" });
  head(s, "The calendar", "12 days · color-coded by pillar");
  docChip(s, "Calendar");
  // legend
  const legend = [[P1, "Video"], [P2, "Sales"], [P3, "Creators"], [P4, "Education"]];
  legend.forEach(([c, l], i) => {
    const x = 0.58 + i * 1.28;
    s.addShape("ellipse", { x, y: 1.42, w: 0.16, h: 0.16, fill: { color: c } });
    s.addText(l, { x: x + 0.22, y: 1.33, w: 1.0, h: 0.3, fontFace: F, fontSize: 10.5, color: MUT, margin: 0 });
  });
  s.addText("PRE-LAUNCH: Mon Aug 24 teaser · Tue 25 countdown", { x: 7.3, y: 1.33, w: 5.5, h: 0.3, fontFace: F, fontSize: 10.5, bold: true, color: P2, align: "right", margin: 0 });

  const days = [
    ["WED 26", "THE DROP", "Demo Video + thread + mailing + KOL campaigns + How-It-Works", [P1, P4], true],
    ["THU 27", "Verified", "thread $1,500 + use cases + one-pager → pipeline", [P2]],
    ["FRI 28", "Network", "thread + comparison visual + Call for Projects + RLPs article", [P2, P4]],
    ["SAT 29", "Debrief", "X Space: creators & partners AMA", [P4]],
    ["MON 31", "Live Demo", "“10 minutes” live build + brief guide", [P4]],
    ["TUE 1", "Creator Video #1", "testimonial + flagship co-created campaign live", [P3, P2]],
    ["WED 2", "Partner Video #2", "community-lead testimonial", [P3]],
    ["THU 3", "Vision", "“Rally, the Hub of Communities”", [P2]],
    ["FRI 4", "Case Study", "“the receipts” + sales article → pipeline + KOL push", [P2]],
    ["SAT 5", "Community Day", "AMA + Campaign Idea Battle (winner funded)", [P3]],
    ["MON 7", "Spotlight", "best community campaigns (every Monday)", [P3]],
    ["TUE 8", "Anatomy", "receipts thread (screenshots) + cutdown", [P1]],
  ];
  const wk = ["LAUNCH · AUG 26 – SEP 1", "SOCIAL PROOF · SEP 2 – 8"];
  for (let r = 0; r < 2; r++) {
    s.addText(wk[r], { x: 0.55, y: 1.78 + r * 2.55, w: 6, h: 0.28, fontFace: F, fontSize: 11, bold: true, color: P2, charSpacing: 2, margin: 0 });
    for (let c = 0; c < 6; c++) {
      const [dd, th, pieces, dots, hero] = days[r * 6 + c];
      const x = 0.55 + c * 2.06, y = 2.1 + r * 2.55;
      s.addShape("roundRect", { x, y, w: 1.96, h: 2.15, rectRadius: 0.08, fill: { color: hero ? DARK : TINT } });
      s.addText(dd, { x: x + 0.15, y: y + 0.12, w: 1.2, h: 0.26, fontFace: F, fontSize: 10.5, bold: true, color: hero ? P1 : MUT, margin: 0 });
      dots.forEach((dc, di) => {
        s.addShape("ellipse", { x: x + 1.42 - di * 0.24, y: y + 0.17, w: 0.15, h: 0.15, fill: { color: dc } });
      });
      s.addText(th, { x: x + 0.15, y: y + 0.42, w: 1.7, h: 0.55, fontFace: F, fontSize: 13, bold: true, color: hero ? WHITE : INK, margin: 0, lineSpacing: 14.5 });
      s.addText(pieces, { x: x + 0.15, y: y + 1.0, w: 1.7, h: 1.05, fontFace: F, fontSize: 9, color: hero ? "E8DCEF" : MUT, margin: 0, lineSpacing: 11 });
    }
  }
}

// ══ 9 · DESIGN REQUESTS ══════════════════════════════════════════════════
{
  const s = pres.addSlide({ masterName: "LIGHT" });
  head(s, "The ask", "What I need from design — all copy is final, design never waits for text");
  docChip(s, "Design requests");
  const groups = [
    ["WAVE 1 · BEFORE THE DROP", "due Aug 21–25", P2, [
      "Demo Video edit (script locked) — the only heavy lift",
      "Teaser 15s + countdown graphic",
      "QT kit for communities, creators & KOLs",
      "OG images (thread + article) + email header",
    ]],
    ["WAVE 2 · LAUNCH WEEK", "due Aug 26–31", P3, [
      "Verified one-pager PDF (the sales asset)",
      "Verified vs Network comparison visual",
      "Call for Projects banner + form header",
      "2 X Space covers · 2 cutdowns · video lower-thirds",
    ]],
    ["WAVE 3 · SOCIAL PROOF", "due Sep 1–3", P4, [
      "Spotlight template (reusable every Monday)",
      "Big-number stat template (case study + numbers posts)",
      "AMA cover + Idea Battle bracket",
    ]],
  ];
  groups.forEach(([g, due, color, items], i) => {
    const x = 0.55 + i * 4.18;
    s.addShape("roundRect", { x, y: 1.55, w: 3.9, h: 4.6, rectRadius: 0.1, fill: { color: i === 0 ? DARK : TINT } });
    const dark = i === 0;
    s.addText(g, { x: x + 0.3, y: 1.82, w: 3.3, h: 0.32, fontFace: F, fontSize: 12.5, bold: true, color: dark ? P1 : P2, margin: 0 });
    s.addText(due, { x: x + 0.3, y: 2.14, w: 3.3, h: 0.3, fontFace: F, fontSize: 10.5, italic: true, color: dark ? "CBB3DC" : MUT, margin: 0 });
    s.addText(items.map((t, j) => ({ text: t, options: { bullet: { code: "2022" }, breakLine: j < items.length - 1 } })),
      { x: x + 0.3, y: 2.6, w: 3.35, h: 3.3, fontFace: F, fontSize: 11.5, color: dark ? WHITE : INK, margin: 0, paraSpaceAfter: 9, lineSpacing: 13.5 });
  });
  s.addText("15 assets · 3 waves · full spec table with per-asset deadlines in the Master Doc §12  ▸",
    { x: 0.55, y: 6.45, w: 12.25, h: 0.35, fontFace: F, fontSize: 12.5, bold: true, color: P2, margin: 0, hyperlink: { url: DOC } });
}

// ══ 9b–9c · DESIGN KIT (already produced) ════════════════════════════════
const DES = path.join(__dirname, "designs");
function thumb(s, file, x, y, w, h, label) {
  s.addShape("roundRect", { x: x - 0.04, y: y - 0.04, w: w + 0.08, h: h + 0.08, rectRadius: 0.06, fill: { color: TINT } });
  s.addImage({ path: path.join(DES, file), x, y, w, h });
  s.addText(label, { x, y: y + h + 0.05, w, h: 0.24, fontFace: F, fontSize: 9, bold: true, color: MUT, margin: 0 });
}
{
  const s = pres.addSlide({ masterName: "LIGHT" });
  head(s, "Design kit · already produced", "Pre-launch & launch day — ready to post");
  docChip(s, "Design kit");
  const W169 = 3.95, H169 = 2.22;
  thumb(s, "teaser_coming_1600x900.png", 0.55, 1.75, W169, H169, "TEASER · MON AUG 24");
  thumb(s, "countdown_rally_3days_1600x900.png", 4.70, 1.75, W169, H169, "COUNTDOWN 3·2·1 · AUG 24–25");
  thumb(s, "launch_og_rally_1600x900.png", 8.85, 1.75, W169, H169, "LAUNCH THREAD OG · WED AUG 26");
  thumb(s, "howitworks_og_rally_1600x900.png", 0.55, 4.42, W169, H169, "“HOW IT WORKS” ARTICLE OG · WED AUG 26");
  thumb(s, "campaigns_are_live_1080x1080.png", 4.70, 4.42, 2.22, 2.22, "LIVE POST · WED AUG 26");
  thumb(s, "email_header_rally_1200x400.png", 7.12, 4.60, 5.55, 1.85, "EMAIL HEADER · WED AUG 26");
}
{
  const s = pres.addSlide({ masterName: "LIGHT" });
  head(s, "Design kit · already produced", "Sales, Spaces & weekly templates");
  docChip(s, "Design kit");
  thumb(s, "verified_onepager_1080x1350.png", 0.55, 1.7, 3.7, 4.63, "VERIFIED ONE-PAGER · THU AUG 27");
  const w = 2.66, h = 1.5, xs = [4.55, 7.37, 10.19], ys = [1.7, 3.62, 5.54];
  thumb(s, "call_for_projects_1600x900.png", xs[0], ys[0], w, h, "CALL FOR PROJECTS · FRI AUG 28");
  thumb(s, "space_livedemo_1600x900.png", xs[1], ys[0], w, h, "SPACE LIVE DEMO · MON AUG 31");
  thumb(s, "space_ama_1600x900.png", xs[2], ys[0], w, h, "CREATORS & PARTNERS AMA · AUG 29");
  thumb(s, "spotlight_template_1600x900.png", xs[0], ys[1], w, h, "SPOTLIGHT TEMPLATE · EVERY MON");
  thumb(s, "casestudy_numbers_template_1600x900.png", xs[1], ys[1], w, h, "CASE STUDY “RECEIPTS” · FRI SEP 4");
  thumb(s, "network_vs_verified_1920x1080.png", xs[2], ys[1], w, h, "NETWORK VS VERIFIED · FRI AUG 28");
  thumb(s, "idea_battle_1080x1080.png", xs[0] + 0.58, ys[2], 1.5, 1.5, "IDEA BATTLE · SAT SEP 5");
  thumb(s, "why_permissionless_1920x1080.png", xs[1], ys[2], w, h, "WHY PERMISSIONLESS · W1");
  s.addShape("roundRect", { x: xs[2], y: ys[2], w, h, rectRadius: 0.06, fill: { color: DARK } });
  s.addText([
    { text: "STILL WITH DESIGN/EDITOR", options: { bold: true, color: P1, fontSize: 9.5, breakLine: true } },
    { text: "Demo Video edit · cutdowns 15/30s · KOL clips · lower-thirds", options: { color: "E8DCEF", fontSize: 9.5 } },
  ], { x: xs[2] + 0.18, y: ys[2] + 0.18, w: w - 0.36, h: h - 0.36, fontFace: F, margin: 0, lineSpacing: 12, valign: "top" });
  s.addText("17 static assets produced in Rally's graphic line — regenerable in minutes (copy, dates, sizes).",
    { x: 0.55, y: 6.78, w: 4.35, h: 0.6, fontFace: F, fontSize: 10.5, italic: true, color: P2, margin: 0, lineSpacing: 12.5 });
}

// ══ 10 · CLOSE ═══════════════════════════════════════════════════════════
{
  const s = pres.addSlide({ masterName: "DARK" });
  s.addImage({ path: path.join(__dirname, "brand/rally_white.png"), x: 5.36, y: 1.35, w: 2.6, h: 0.62 });
  s.addText("“The campaign button belongs\nto everyone now.”", { x: 1.2, y: 2.6, w: 10.9, h: 1.7, fontFace: F, fontSize: 38, bold: true, color: WHITE, align: "center", margin: 0, lineSpacing: 46 });
  s.addText("4 pillars · 3 objectives · 12 days · everything written.", { x: 1.2, y: 4.4, w: 10.9, h: 0.45, fontFace: F, fontSize: 17, color: "E8DCEF", align: "center", margin: 0 });
  s.addText("Greenlight this week = we ship Wednesday Aug 26.", { x: 1.2, y: 4.95, w: 10.9, h: 0.45, fontFace: F, fontSize: 17, italic: true, color: P1, align: "center", margin: 0 });
  s.addText("Master Doc — plan, copy, scripts, design  ▸", { x: 1.2, y: 6.0, w: 10.9, h: 0.4, fontFace: F, fontSize: 13, bold: true, color: "B79ACB", align: "center", margin: 0, hyperlink: { url: DOC } });
}

pres.writeFile({ fileName: path.join(__dirname, "Rally_Permissionless_Campaigns_Plan.pptx") })
  .then(() => console.log("deck written"));
