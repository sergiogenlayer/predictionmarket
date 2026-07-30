#!/usr/bin/env python3
"""Build the Permissionless Campaigns activation calendar (Rally / GenLayer),
replicating the weekly-block format of the existing Rally campaign calendar sheet."""

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUT = "/tmp/claude-0/-home-user-predictionmarket/cadac25f-7355-5a2e-945b-6583f4b657ab/scratchpad/permissionless_campaigns_calendar.xlsx"

FONT = "Arial"
thin = Side(style="thin", color="B7B7B7")
border = Border(left=thin, right=thin, top=thin, bottom=thin)

f_base = Font(name=FONT, size=10)
f_bold = Font(name=FONT, size=10, bold=True)
f_white_bold = Font(name=FONT, size=10, bold=True, color="FFFFFF")
f_title = Font(name=FONT, size=12, bold=True, color="FFFFFF")

fill_week = PatternFill("solid", fgColor="134F5C")   # dark teal week banners
fill_days = PatternFill("solid", fgColor="D9D9D9")   # day header row
fill_cat = PatternFill("solid", fgColor="EFEFEF")    # category column
fill_action = PatternFill("solid", fgColor="FCE5CD") # action release cells
fill_annc = PatternFill("solid", fgColor="D9EAD3")   # announcement cells
fill_title = PatternFill("solid", fgColor="0B3040")

wrap = Alignment(wrap_text=True, vertical="top", horizontal="left")
center = Alignment(wrap_text=True, vertical="center", horizontal="center")

wb = Workbook()
ws = wb.active
ws.title = "Permissionless Campaigns"

# Column widths: A category, B-H days, I total
ws.column_dimensions["A"].width = 20
for c in range(2, 9):
    ws.column_dimensions[get_column_letter(c)].width = 26
ws.column_dimensions["I"].width = 12

# ---------------------------------------------------------------- title row
ws.merge_cells("A1:I1")
ws["A1"] = "PERMISSIONLESS CAMPAIGNS — ACTIVATION CALENDAR · Aug 3 – Sep 6, 2026"
ws["A1"].font = f_title
ws["A1"].fill = fill_title
ws["A1"].alignment = center
ws.row_dimensions[1].height = 28

# ---------------------------------------------------------------- day header
days = ["Category", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "TOTAL ($)"]
for i, d in enumerate(days, start=1):
    c = ws.cell(row=2, column=i, value=d)
    c.font = f_bold
    c.fill = fill_days
    c.alignment = center
    c.border = border
ws.freeze_panes = "B3"

# ---------------------------------------------------------------- content
# Each week: (banner, {category: [mon..sun]}, total)
CHANNELS = ["Action Release", "Internal Campaigns", "", "Announcement", "X",
            "Mailing", "KOL", "Wallets", "Discord", "Telegram"]

weeks = [
    (
        "Week of Aug 03 – Aug 09, 2026 (TEASER + PERMISSIONLESS NARRATIVE)",
        {
            "Action Release": ["", "", "", "", "Teaser Drop", "", ""],
            "Internal Campaigns": [
                "Permission Denied — worst 'no' you ever got from a brand or platform (500$)",
                "Pitch Your Campaign in 5 Words",
                "The Campaign That Should Exist (1000$)",
                "The Gatekeeper's Obituary",
                "Your Brand Has $500. Launch Something. (500$)",
                "The Leak — write the fake announcement",
                "Locked Prediction: what happens when anyone can launch a campaign?",
            ],
            "": [
                "The Rejection Letter", "The Elevator Pitch", "The Fine Print",
                "The Waitlist", "The Green Light", "The Side Quest", "The Sunday Take",
            ],
            "Announcement": ["", "", "", "", "Something permissionless is coming (TEASER VIDEO)", "", "Countdown begins (POST)"],
            "X": ["", "", "", "", "", "", ""],
            "Mailing": ["", "", "", "", "", "", ""],
            "KOL": ["", "", "", "", "", "", ""],
            "Wallets": ["", "", "", "", "", "", ""],
            "Discord": ["Leaderboard Spotlight", "", "", "", "", "", "Cryptic teaser drop"],
            "Telegram": ["", "", "", "", "Teaser forward", "", ""],
        },
        "2,000$",
    ),
    (
        "Week of Aug 10 – Aug 16, 2026 (ANNOUNCEMENT + EDUCATION)",
        {
            "Action Release": ["PERMISSIONLESS KICK OFF", "", "", "", "", "", ""],
            "Internal Campaigns": [
                "Permissionless Manifesto — announcement day",
                "Explain Permissionless Campaigns in 2 Sentences (500$)",
                "The First Campaign You'd Launch (1000$)",
                "Brands vs Creators — who wins permissionless?",
                "Stump the Validators (500$)",
                "Bring a Builder — tag someone who should launch a campaign",
                "The Acceptance Speech — you just launched your first campaign",
            ],
            "": [
                "The Onboarding", "The Tutorial Speedrun", "Red Flag, Green Flag: campaigns edition",
                "The Group Chat Take", "The Unhinged Campaign Idea", "The Worst Brief",
                "Campaigns for a 10-Year-Old",
            ],
            "Announcement": [
                "PERMISSIONLESS CAMPAIGNS ANNOUNCEMENT (VIDEO)",
                "How it works (ARTICLE)",
                "Step-by-step: launch your campaign (TUTORIAL)",
                "Use case #1: Creators (ARTICLE)",
                "Use case #2: Brands (ARTICLE)",
                "Use case #3: Communities & DAOs (ARTICLE)",
                "",
            ],
            "X": ["", "", "", "", "", "X Space: The End of Gatekeepers", ""],
            "Mailing": ["Announcement newsletter", "", "", "", "", "", ""],
            "KOL": ["Amplification", "", "", "", "", "", ""],
            "Wallets": ["", "", "", "", "", "", ""],
            "Discord": ["", "", "Walkthrough + AMA", "", "", "", "How to launch a campaign (each week)"],
            "Telegram": ["Announcement push", "", "", "", "", "", ""],
        },
        "2,000$",
    ),
    (
        "Week of Aug 17 – Aug 23, 2026 (LAUNCH WEEK — CAMPAIGNS LIVE)",
        {
            "Action Release": ["PERMISSIONLESS CAMPAIGNS LIVE", "", "", "", "", "", ""],
            "Internal Campaigns": [
                "Launch Day — first 10 community campaigns get featured (1000$)",
                "Launch a Campaign, Win the Pot (1000$)",
                "Campaign Showcase #1 — community picks",
                "The Remix — improve an existing campaign (500$)",
                "Money Opportunity campaign (2000$)",
                "The Campaign Wars — head-to-head vote-off (500$)",
                "The 6AM Take: permissionless edition",
            ],
            "": [
                "The Press Release", "The Origin Story", "The Twist Ending",
                "The Verdict", "The Founder Mode", "The Wrong Take", "The Eulogy (for gatekeeping)",
            ],
            "Announcement": [
                "WE ARE LIVE (POST + VIDEO)", "", "First campaigns showcase (POST)",
                "", "Creator spotlight (ARTICLE)", "", "",
            ],
            "X": ["", "", "", "", "", "X Space with first campaign creators", ""],
            "Mailing": ["We're live", "", "", "", "", "", ""],
            "KOL": ["Amplification", "", "", "Amplification", "", "", ""],
            "Wallets": ["Permissionless campaigns live", "", "", "", "", "", ""],
            "Discord": ["Launch party + Leaderboard Spotlight", "", "", "", "", "", "How to launch a campaign (each week)"],
            "Telegram": ["Live push", "", "", "", "", "", ""],
        },
        "5,000$",
    ),
    (
        "Week of Aug 24 – Aug 30, 2026 (PERMISSIONLESS x PARTNERS & CREATORS)",
        {
            "Action Release": ["", "", "", "", "", "", ""],
            "Internal Campaigns": [
                "Partner Campaign #1 kick off (1000$)",
                "Co-create with Wingston — best campaign brief (500$)",
                "Campaign Showcase #2 — rarest campaigns",
                "Partner Campaign #2 (1000$)",
                "The Collab — creators x brands matchmaking",
                "The Vision: campaigns in 2030 (500$)",
                "The Final Boss — hardest campaign to win",
            ],
            "": [
                "The Memoir", "The Apology", "The Underrated",
                "The Push Notification", "The Yelp Review", "The Group Chat Name", "The Trade Off",
            ],
            "Announcement": [
                "Partner campaign #1 (POST)", "", "Campaign showcase (POST)",
                "Partner campaign #2 (POST)", "", "The vision of permissionless (ARTICLE)", "",
            ],
            "X": ["", "", "", "", "", "X Space with partners & creators", ""],
            "Mailing": ["", "", "", "", "", "", ""],
            "KOL": ["", "Amplification", "", "", "", "", ""],
            "Wallets": ["", "", "", "", "", "", ""],
            "Discord": ["Leaderboard Spotlight", "", "", "", "", "", ""],
            "Telegram": ["", "", "", "", "", "", ""],
        },
        "3,000$",
    ),
    (
        "Week of Aug 31 – Sep 06, 2026 (MOMENTUM + NUMBERS)",
        {
            "Action Release": ["Campaign Analytics Release", "", "", "", "", "", ""],
            "Internal Campaigns": [
                "Hype Campaign (show numbers)",
                "Best Campaign Awards — community vote (1000$)",
                "The Retrospective — what did we learn",
                "Your Campaign, Amplified — winners get official repost",
                "Hall of Fame induction (500$)",
                "Hype Campaign (show numbers)",
                "What's Next — roadmap tease",
            ],
            "": [
                "The Yearbook Quote", "The Out of Office", "The Wikipedia Line",
                "The Toast", "The Voice Note", "The Disclaimer", "The Plot Twist",
            ],
            "Announcement": [
                "Numbers so far (POST)", "Best Campaign Awards (POST)", "",
                "", "Hall of Fame (POST)", "", "What's next (POST)",
            ],
            "X": ["", "", "", "", "", "X Space: month in review", ""],
            "Mailing": ["", "", "", "", "Monthly recap", "", ""],
            "KOL": ["Amplification", "", "", "", "", "", ""],
            "Wallets": ["", "", "", "", "", "", ""],
            "Discord": ["Spotlight Leaderboard", "Awards vote", "", "", "", "", ""],
            "Telegram": ["", "Vote push", "", "", "", "", ""],
        },
        "1,500$",
    ),
]

row = 3
for banner, data, total in weeks:
    # merged week banner
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=8)
    b = ws.cell(row=row, column=1, value=banner)
    b.font = f_white_bold
    b.fill = fill_week
    b.alignment = center
    for c in range(1, 10):
        ws.cell(row=row, column=c).border = border
    ws.row_dimensions[row].height = 22
    row += 1

    for ch in CHANNELS:
        cat = ws.cell(row=row, column=1, value=ch)
        cat.font = f_bold
        cat.fill = fill_cat
        cat.alignment = wrap
        cat.border = border
        vals = data.get(ch, [""] * 7)
        for i, v in enumerate(vals):
            cell = ws.cell(row=row, column=2 + i, value=v)
            cell.font = f_base
            cell.alignment = wrap
            cell.border = border
            if v and ch == "Action Release":
                cell.fill = fill_action
                cell.font = f_bold
            elif v and ch == "Announcement":
                cell.fill = fill_annc
        tot = ws.cell(row=row, column=9, value=total if ch == "Internal Campaigns" else "")
        tot.font = f_bold
        tot.alignment = center
        tot.border = border
        if ch in ("Internal Campaigns", ""):
            ws.row_dimensions[row].height = 55
        row += 1
    row += 1  # blank spacer row between weeks

# ---------------------------------------------------------------- grand total
g = ws.cell(row=row, column=8, value="TOTAL CAMPAIGN")
g.font = f_bold
g.alignment = Alignment(horizontal="right", vertical="center")
gt = ws.cell(row=row, column=9, value="13,500$")
gt.font = f_bold
gt.alignment = center
gt.border = border
gt.fill = fill_days
row += 2

# ---------------------------------------------------------------- legend & links
notes = [
    ("How to read this calendar", ""),
    ("Budgets", "Amounts in parentheses (e.g. 500$) are the paid pot of that campaign. TOTAL ($) sums the week's paid pots. Campaigns without an amount run on Rally Points."),
    ("Internal Campaigns (row 1)", "Launch-specific activation of the permissionless narrative."),
    ("Internal Campaigns (row 2)", "Always-on daily prompt in the standard Rally format."),
    ("Phases", "W1 Teaser → W2 Announcement + Education → W3 Launch → W4 Partners & Creators → W5 Momentum + Numbers."),
    ("", ""),
    ("Internal Campaigns doc", "https://docs.google.com/document/d/13DhJE-HBozbZijic54TgX2L6m8FPw_oHp-_uZ1aOzuQ/edit?usp=sharing"),
    ("Rally Tracker", "https://rally-tracker-ten.vercel.app/"),
]
for label, text in notes:
    a = ws.cell(row=row, column=1, value=label)
    a.font = f_bold
    a.alignment = wrap
    ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=8)
    b = ws.cell(row=row, column=2, value=text)
    b.font = f_base
    b.alignment = wrap
    row += 1

wb.save(OUT)
print("saved", OUT)
