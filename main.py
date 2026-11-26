#!/usr/bin/env python3
"""The World Today - one-image summary of Thursday 26 November 2026.

Pure standard-library procedural newspaper front page, drawn pixel by
pixel and encoded as a hand-written PNG (zlib + struct only).
Writes entry.png to MAKEFUN_OUTPUT_DIR (or /output). Deterministic.

Story count: 31
  4 hero stories (COP31 collapse, Cairo tanker fire, Ukraine hits
  Russian jets, Russian strikes on Ukraine energy grid)
  24 grid cards
  3 ticker stories (DR Congo Ebola toll, US Thanksgiving,
  Democrats clinch US House majority)
"""
import os
import struct
import zlib

W = 1024
H = 1024

# palette - warm paper, deep ink, editorial accents
PAPER = (246, 241, 229)
PAPER_DARK = (236, 228, 205)
INK = (20, 22, 28)
NAVY = (16, 38, 80)
RED = (172, 30, 36)
CRIMSON = (140, 22, 30)
GOLD = (148, 104, 18)
TEAL = (14, 92, 92)
GREEN = (26, 104, 50)
PURPLE = (88, 50, 128)
GREY = (58, 58, 54)
WHITE = (255, 255, 255)
BLACK = (8, 8, 10)
SEA = (34, 88, 136)
SKYBG = (219, 233, 248)
REDBG = (250, 226, 220)
GREENBG = (222, 240, 224)
SANDBG = (244, 232, 196)
FIRE = (232, 110, 30)
SMOKE = (110, 108, 104)

PX = bytearray(W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        PX[i] = c[0]
        PX[i + 1] = c[1]
        PX[i + 2] = c[2]


def rect(x, y, w, h, c):
    x0 = max(x, 0)
    x1 = min(x + w, W)
    y0 = max(y, 0)
    y1 = min(y + h, H)
    for yy in range(y0, y1):
        base = yy * W
        for xx in range(x0, x1):
            i = (base + xx) * 3
            PX[i] = c[0]
            PX[i + 1] = c[1]
            PX[i + 2] = c[2]


def hline(x, y, w, c, t=2):
    rect(x, y, w, t, c)


def vline(x, y, h, c, t=2):
    rect(x, y, t, h, c)


def seg(x0, y0, x1, y1, c, t=2):
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for s in range(steps + 1):
        x = x0 + (x1 - x0) * s // steps
        y = y0 + (y1 - y0) * s // steps
        rect(x - t // 2, y - t // 2, t, t, c)


def disc(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                px(xx, yy, c)


def tri(x0, y0, x1, y1, x2, y2, c):
    minx = max(min(x0, x1, x2), 0)
    maxx = min(max(x0, x1, x2), W - 1)
    miny = max(min(y0, y1, y2), 0)
    maxy = min(max(y0, y1, y2), H - 1)
    d = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    if d == 0:
        return
    for yy in range(miny, maxy + 1):
        for xx in range(minx, maxx + 1):
            a = ((y1 - y2) * (xx - x2) + (x2 - x1) * (yy - y2)) / d
            b = ((y2 - y0) * (xx - x2) + (x0 - x2) * (yy - y2)) / d
            if a >= 0 and b >= 0 and 1.0 - a - b >= 0:
                px(xx, yy, c)


# 5x7 bitmap font, drawn from scratch for this entry
FONT = {
 "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
 "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
 "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
 "D": ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
 "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
 "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
 "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
 "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
 "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
 "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
 "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
 "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
 "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
 "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
 "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
 "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
 "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
 "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
 "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
 "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
 "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
 "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
 "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
 "X": ("10001", "01010", "00100", "00100", "00100", "01010", "10001"),
 "Y": ("10001", "01010", "00100", "00100", "00100", "00100", "00100"),
 "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
 "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
 "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
 "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
 "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
 "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
 "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
 "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
 "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
 "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
 "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
 " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
 ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
 ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
 "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
 "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
 "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
 "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
 "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
 "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
 ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
 ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
 "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
 "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
 "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
 ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
}


def text_w(s, sc):
    return len(s) * 6 * sc - sc


def draw_text(x, y, s, c, sc=2):
    cx = x
    for ch in s.upper():
        g = FONT.get(ch, FONT[" "])
        for r in range(7):
            row = g[r]
            for col in range(5):
                if row[col] == "1":
                    rect(cx + col * sc, y + r * sc, sc, sc, c)
        cx += 6 * sc
    return cx


def centered(y, s, c, sc=2):
    draw_text((W - text_w(s, sc)) // 2, y, s, c, sc)


def wrap(s, maxchars):
    lines = []
    cur = ""
    for word in s.split():
        trial = (cur + " " + word).strip()
        if len(trial) <= maxchars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(x, y, s, c, sc, maxchars, maxlines, lh=None):
    if lh is None:
        lh = 8 * sc + 2
    ls = wrap(s, maxchars)
    for i, ln in enumerate(ls[:maxlines]):
        draw_text(x, y + i * lh, ln, c, sc)
    return y + min(len(ls), maxlines) * lh


# ---------------- background ----------------
rect(0, 0, W, H, PAPER)
for yy in range(0, H, 4):
    rect(0, yy, W, 1, PAPER_DARK)

# ---------------- masthead ----------------
hline(10, 6, W - 20, INK, 4)
centered(12, "THE WORLD TODAY", NAVY, 5)
centered(54, "THURSDAY 26 NOVEMBER 2026 - ALL THE DAY'S NEWS ON ONE PAGE", RED, 2)
centered(76, "31 STORIES - CLIMATE - WAR - MARKETS - SPACE - COURTS - HEALTH - DIPLOMACY", INK, 1)
hline(10, 90, W - 20, INK, 3)

# ---------------- hero row ----------------
HY = 96
HH = 132
# Hero 1 (wide, left): COP31 collapse in Turkiye
rect(10, HY, 500, HH, SKYBG)
vline(10, HY, HH, NAVY, 3)
vline(507, HY, HH, NAVY, 3)
hline(10, HY, 500, NAVY, 3)
hline(10, HY + HH - 3, 500, NAVY, 3)
draw_text(22, HY + 7, "CLIMATE SUMMIT - TURKIYE", RED, 1)
para(22, HY + 19, "COP31 ENDS WITH NO DEAL AT ALL", INK, 2, 40, 1)
para(22, HY + 40, "FIRST COP TO FAIL TO ADOPT A DEAL SINCE COPENHAGEN 2009. TALKS RAN 48 HOURS OVER; THE EU REJECTED A TEXT WITH NO FOSSIL FUEL PHASE-OUT WORDING.", GREY, 1, 76, 4)
# broken globe icon beside the verdict line
disc(46, HY + 104, 17, SEA)
disc(46, HY + 104, 13, TEAL)
seg(40, HY + 90, 48, HY + 102, INK, 2)
seg(48, HY + 102, 42, HY + 112, INK, 2)
seg(42, HY + 112, 50, HY + 120, INK, 2)
para(72, HY + 100, "DIPLOMATS CALL IT THE WORST COP EVER HELD.", CRIMSON, 1, 70, 1)

# Hero 2 (top right): Cairo fuel tanker fire
rect(522, HY, 492, 62, REDBG)
vline(522, HY, 62, RED, 3)
hline(522, HY, 492, RED, 3)
# flame icon
tri(538, HY + 48, 550, HY + 24, 562, HY + 48, FIRE)
tri(544, HY + 48, 550, HY + 34, 556, HY + 48, GOLD)
draw_text(572, HY + 6, "EGYPT - CAIRO RING ROAD", RED, 1)
para(572, HY + 17, "FUEL TANKER FIRE KILLS 31", INK, 2, 36, 1)
para(572, HY + 36, "TANKER BLAZE ON THE RING ROAD LEAVES MORE THAN 20 INJURED.", GREY, 1, 72, 2)

# Hero 3+4 (bottom right, split): Ukraine war, both directions
rect(522, HY + 70, 242, 62, SANDBG)
vline(522, HY + 70, 62, GOLD, 3)
hline(522, HY + 70, 242, GOLD, 3)
draw_text(532, HY + 76, "WAR - UKRAINE STRIKES", GOLD, 1)
para(532, HY + 87, "KYIV HITS 5 RUSSIAN JETS", INK, 1, 38, 2, lh=9)
para(532, HY + 107, "JETS STRUCK AT SAVASLEYKA AIR BASE IN RUSSIA.", GREY, 1, 38, 2, lh=9)

rect(772, HY + 70, 242, 62, REDBG)
vline(772, HY + 70, 62, CRIMSON, 3)
hline(772, HY + 70, 242, CRIMSON, 3)
draw_text(782, HY + 76, "WAR - ENERGY GRID HIT", CRIMSON, 1)
para(782, HY + 87, "RUSSIAN STRIKES KILL 5", INK, 1, 38, 2, lh=9)
para(782, HY + 107, "POWER CUT ACROSS 5 REGIONS AS ENERGY SITES HIT.", GREY, 1, 38, 2, lh=9)
hline(10, HY + HH + 5, W - 20, INK, 3)

# ---------------- grid cards ----------------
CARDS = [
 ("TRADE", TEAL, "US CAPS INDIA TARIFF AT 17% IF DEAL LANDS",
  "USTR: 17% WITH A DEAL, 25% WITHOUT. TALKS GO ON."),
 ("ENERGY", TEAL, "OIL JUMPS AS HOUTHIS CLAIM SAUDI REFINERY HIT",
  "CLAIM TARGETS SAUDI ARABIA'S LARGEST REFINERY."),
 ("CONFLICT", RED, "TWO TANKERS STRIKE SEA MINES IN HORMUZ",
  "IRANIAN REPORTS SAY MINES HIT BOTH SHIPS IN THE STRAIT."),
 ("CONFLICT", RED, "TRUMP: US CAN FUND IRAN WAR TO END OF JANUARY",
  "WASHINGTON SAYS MONEY IS THERE IF THE WAR DRAGS ON."),
 ("SPACE", NAVY, "PAKISTAN ASTRONAUT FIRST FOREIGNER ON TIANGONG",
  "ZEESHAN ALI FLIES ON SHENZHOU-24 TO CHINA'S STATION."),
 ("PACIFIC", NAVY, "SOLOMON ISLANDS SIGN AUSTRALIA SECURITY PACT",
  "DEAL BARS FOREIGN BASES: A SETBACK FOR CHINA."),
 ("AMERICAS", TEAL, "PLANE CRASH OFF MISSISSIPPI KILLS SIX",
  "SIX DEAD, TWO OF THEM CHILDREN, OFF THE COAST."),
 ("AMERICAS", TEAL, "COLOMBIA POLICE FREE 20 SUPERMARKET HOSTAGES",
  "RAID ENDS A 17-HOUR STANDOFF; ALL 20 FREED."),
 ("WEATHER", GREEN, "CALIFORNIA WARNS OF KING TIDE FLOODING",
  "THANKSGIVING FLOOD WARNING AS TIDES PEAK."),
 ("JUSTICE", PURPLE, "JUDGE URGES DROPPING TOP NETANYAHU CHARGE",
  "ISRAELI JUDGE FLOATS CUTTING THE GRAVEST COUNT IN THE TRIAL."),
 ("ISRAEL", NAVY, "KNESSET BACKS COMMISSION INTO 7 OCTOBER FAILINGS",
  "LAWMAKERS APPROVE A FORMAL INQUIRY COMMISSION."),
 ("CLIMATE", GREEN, "NORWAY TOP COURT VOIDS DISPUTED OIL PERMITS",
  "SUPREME COURT CANCELS LICENCES IN CLIMATE CASE."),
 ("HEALTH", GREEN, "KENYA DISCHARGES ITS LAST EBOLA PATIENT",
  "FINAL PATIENT GOES HOME AS OUTBREAK WINDS DOWN."),
 ("AFRICA", GOLD, "GHANA LAUNCHES HERITAGE SERIES BANKNOTES",
  "NEW NOTES HONOUR NKRUMAH AND KOFI ANNAN."),
 ("DEFENCE", NAVY, "RAF SHELTERS JETS NIGHTLY OVER DRONE FEAR",
  "JETS MOVED INTO HANGARS EVERY NIGHT FOR FEAR OF DRONES."),
 ("ASIA", NAVY, "US DEPORTED 1,700 INDIANS THROUGH 2026",
  "FIGURE GIVEN BY INDIA'S FOREIGN MINISTRY."),
 ("UKRAINE", GOLD, "MELANIA TRUMP REUNITES 9 MORE WAR CHILDREN",
  "NINE CHILDREN SEPARATED BY THE WAR REJOIN FAMILIES."),
 ("BRITAIN", PURPLE, "UK OPENS INQUIRY INTO NUCLEAR TEST VETERANS",
  "INDEPENDENT PROBE INTO EFFECTS ON TEST VETERANS."),
 ("EUROPE", NAVY, "GERMANY TO REBUILD EAGLE'S NEST AFTER FIRE",
  "HISTORIC MOUNTAIN SITE TO RISE AGAIN AFTER BLAZE."),
 ("US ARMY", GREY, "US TROOPS DETONATE 68 BARRELS OF OLD LEAD AZIDE",
  "AGEING EXPLOSIVE STOCK DESTROYED IN A BLAST."),
 ("ASIA", NAVY, "HONG KONG MARKS A YEAR SINCE ITS DEADLIEST FIRE",
  "CITY REMEMBERS VICTIMS ONE YEAR ON FROM THE BLAZE."),
 ("AFRICA", GOLD, "RAMAPHOSA CLEARS FARMGATE IMPEACHMENT PROBE",
  "SOUTH AFRICA'S PRESIDENT SURVIVES THE INQUIRY."),
 ("EUROPE", NAVY, "PUIGDEMONT TO RETURN TO SPAIN ON 12 DECEMBER",
  "CATALAN LEADER SETS A DATE TO COME HOME."),
 ("TECH", PURPLE, "AI CHATBOT 'THREAT' SCREENSHOT GOES VIRAL",
  "IMAGE OF A CHATBOT MENACING A USER SPREADS ONLINE."),
]

GX = 10
GY = 240
CW = 331
CHH = 80
GAPX = 7
GAPY = 4
for i, (tag, tc, head, body) in enumerate(CARDS):
    col = i % 3
    row = i // 3
    x = GX + col * (CW + GAPX)
    y = GY + row * (CHH + GAPY)
    rect(x, y, CW, CHH, WHITE)
    vline(x, y, CHH, tc, 3)
    hline(x, y, CW, tc, 2)
    draw_text(x + 8, y + 4, tag, tc, 1)
    para(x + 8, y + 14, head, INK, 2, 26, 2, lh=17)
    para(x + 8, y + 50, body, GREY, 1, 52, 3, lh=9)

# ---------------- ticker ----------------
TY = GY + 8 * (CHH + GAPY) + 8
rect(10, TY, W - 20, H - TY - 8, INK)
draw_text(20, TY + 7, "ALSO TODAY - THURSDAY 26 NOVEMBER 2026", GOLD, 2)
TICKER = [
 "HEALTH: EBOLA DEATH TOLL IN DR CONGO PASSES 5,300 AS KENYA CLEARS ITS LAST CASE",
 "UNITED STATES: FAMILIES MARK THANKSGIVING, WITH KING TIDE FLOODS THREATENING CALIFORNIA",
 "WASHINGTON: DEMOCRATS LOCK UP A HOUSE MAJORITY OF AT LEAST 258 SEATS, AP REPORTS",
]
for i, t in enumerate(TICKER):
    y = TY + 30 + i * 15
    rect(20, y + 2, 6, 6, GOLD)
    draw_text(34, y, t, WHITE, 1)
draw_text(20, TY + 80, "THE WORLD TODAY - ONE PAGE, ONE DAY: THURSDAY 26 NOVEMBER 2026 - 31 STORIES", PAPER_DARK, 1)

# ---------------- write PNG ----------------
def chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


raw = b""
for yy in range(H):
    raw += b"\x00" + bytes(PX[yy * W * 3:(yy + 1) * W * 3])
png = b"\x89PNG\r\n\x1a\n"
png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
png += chunk(b"IDAT", zlib.compress(raw, 9))
png += chunk(b"IEND", b"")

outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
os.makedirs(outdir, exist_ok=True)
path = os.path.join(outdir, "entry.png")
with open(path, "wb") as f:
    f.write(png)
print("wrote", path, len(png), "bytes")
