#!/usr/bin/env python3
"""draw.py - renders entry.png: a broadsheet front page summing up the world
news of Friday 20 November 2026. Python + Pillow only. Fully deterministic:
no randomness, no timestamps - running it twice gives byte-identical output.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
FD = "/usr/share/fonts/truetype/dejavu/"
SERIF_B = FD + "DejaVuSerif-Bold.ttf"
SANS = FD + "DejaVuSans.ttf"
SANS_B = FD + "DejaVuSans-Bold.ttf"

PAPER = (247, 241, 227)
INK = (26, 23, 18)
RED = (179, 32, 42)
DARKRED = (140, 22, 32)
GREY = (90, 84, 74)
RULE = (60, 54, 44)
WHITE = (255, 255, 255)

REGION_COLORS = {
    "Europe": (51, 86, 127),
    "Asia": (181, 84, 30),
    "Middle East": (138, 109, 31),
    "Africa": (62, 122, 58),
    "Americas": (160, 58, 91),
    "Oceania": (42, 122, 122),
    "Global": (85, 80, 73),
}
REGIONS = [("EUROPE", 8), ("ASIA", 8), ("MIDDLE EAST", 3), ("AFRICA", 5),
           ("AMERICAS", 4), ("OCEANIA", 3), ("GLOBAL", 4)]

_cache = {}


def F(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def tw(d, s, font):
    return d.textlength(s, font=font)


def fit_font(d, s, path, start, min_size, max_w):
    size = start
    while size > min_size and tw(d, s, F(path, size)) > max_w:
        size -= 1
    return F(path, size)


def wrap(d, s, font, max_w):
    words = s.split()
    lines, cur = [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if tw(d, t, font) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def text_block(d, x, y, s, font, max_w, lh, fill=INK, max_lines=None):
    lines = wrap(d, s, font, max_w)
    if max_lines:
        lines = lines[:max_lines]
    for i, ln in enumerate(lines):
        d.text((x, y + i * lh), ln, font=font, fill=fill)
    return y + len(lines) * lh


def badge(d, cx, cy, r, num):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED, outline=WHITE, width=2)
    f = F(SANS_B, r + 2)
    s = str(num)
    w_ = tw(d, s, f)
    d.text((cx - w_ / 2, cy - (r + 2) / 2 - 2), s, font=f, fill=WHITE)


def source_tag(d, box, s):
    x0, y0, x1, y1 = box
    f = F(SANS_B, 10)
    w_ = tw(d, s, f) + 10
    d.rectangle([x1 - w_, y1 - 16, x1, y1], fill=(20, 18, 14))
    d.text((x1 - w_ + 5, y1 - 14), s, font=f, fill=(245, 240, 225))


# ---------------------------------------------------------------- stories
HEROES = [
    dict(num=1, tag="KYIV, UKRAINE - WAR", region="Europe",
         head="Missiles Shatter Kyiv's Bridges in a Night of Fire",
         body="Some 110 missiles and 400 drones struck overnight; at least nine "
              "people died, and power and water failed across the capital.",
         src="Kyiv Independent / BBC", art="kyiv"),
    dict(num=2, tag="ODISHA, INDIA - CYCLONE", region="Asia",
         head="Cyclone Akvan Roars Ashore at Gopalpur",
         body="The storm crossed the coast from 8 am, gusting to 90 km/h. Over "
              "300,000 people had been moved to shelters; no deaths reported.",
         src="IMD / Deccan Herald", art="cyclone"),
    dict(num=3, tag="TAIPEI - SEOUL - TOKYO - MARKETS", region="Asia",
         head="AI Sell-Off Sinks Asia's Stock Markets",
         body="Taiwan fell 6.2% to end its worst week since 1991; Seoul lost "
              "5.2% and Tokyo 5.1% as chip stocks led the rout.",
         src="Al Jazeera / Anadolu", art="markets"),
]

BRIEFS = [
    dict(num=4, tag="BRUSSELS - DIPLOMACY", region="Europe",
         head="Britain and EU Seal a Reset Deal",
         body="Food checks ease; 100,000 youth visas a year; carbon markets linked.",
         src="Reuters", art="eu"),
    dict(num=5, tag="ANTALYA - CLIMATE", region="Global",
         head="COP31's Last Day Ends With No Deal",
         body="The draft text leaves out fossil fuels; talks ran past the deadline.",
         src="UN News", art="cop"),
    dict(num=6, tag="EASTERN POLAND - SECURITY", region="Europe",
         head="Russian Missile Lands in a Polish Field",
         body="A cruise missile came down in farmland; two airports paused flights.",
         src="Reuters", art="poland"),
    dict(num=7, tag="CENTRAL IRAQ - SECURITY", region="Middle East",
         head="Army Enters Militia Stronghold",
         body="Iraqi troops moved into Jurf al-Sakhar, long held by armed groups.",
         src="Reuters", art="iraq"),
    dict(num=8, tag="ITALY - LABOUR", region="Europe",
         head="General Strike Grips Italy",
         body="Workers and students marched against the government's budget plans.",
         src="Reuters", art="italy"),
    dict(num=9, tag="TOKYO - ECONOMY", region="Asia",
         head="Japan Inflation Quickens to 2.3%",
         body="October's rise keeps a December rate increase in view.",
         src="Reuters", art="japan"),
    dict(num=10, tag="SEOUL - POLITICS", region="Asia",
         head="Ruling Party to Impeach Top Judge",
         body="The move follows a court ruling that overturned a conviction.",
         src="Korea Herald", art="korea"),
    dict(num=11, tag="TURKANA, KENYA - ENERGY", region="Africa",
         head="Kenya Drills Its First Oil Well",
         body="First crude from the Turkana fields is due on 1 December.",
         src="allAfrica", art="kenya"),
    dict(num=12, tag="WASHINGTON - TRADE", region="Americas",
         head="Trump: Mexico Trade Deal Is Close",
         body="After meeting Sheinbaum, he said talks with Canada lag behind.",
         src="Bloomberg", art="trade"),
    dict(num=13, tag="WELLINGTON - CRICKET", region="Oceania",
         head="Phillips' 118 Completes a Rare Set",
         body="Hundreds against India in all three formats in one year - a first.",
         src="ICC", art="cricket"),
]

INDEX = [
    (14, "LVIV", "Station strike kills two", "BBC", "Europe"),
    (15, "MOSCOW", "Estonia border closure decreed", "Reuters", "Europe"),
    (16, "BERLIN", "Pupils strike over military service", "Al Jazeera", "Europe"),
    (17, "LONDON", "General: UK runs cyber attacks abroad", "Sky News", "Europe"),
    (18, "BEIJING", "Loan rates held for an 18th month", "Xinhua", "Asia"),
    (19, "TOKYO", "SoftBank slides over 14% in a day", "Al Jazeera", "Asia"),
    (20, "SEOUL", "Kospi ends the week 7.9% lower", "Anadolu", "Asia"),
    (21, "GANJAM", "209 mm of rain as Akvan crossed", "PTI", "Asia"),
    (22, "LEBANON", "Israeli strikes hit south and east", "Anadolu", "Middle East"),
    (23, "YEMEN", "Gunmen fire on a cargo ship offshore", "UKMTO", "Middle East"),
    (24, "ABUJA", "Court bars new evidence vs Tinubu", "Channels TV", "Africa"),
    (25, "KAMPALA", "Police to enforce Ebola rally ban", "allAfrica", "Africa"),
    (26, "MALAWI", "Night-long petrol queues in fuel crisis", "Al Jazeera", "Africa"),
    (27, "AFRICA", "AfDB: 22 nations in debt distress", "allAfrica", "Africa"),
    (28, "LAS VEGAS", "Russell fastest in wet GP practice", "Autosport", "Americas"),
    (29, "NEW YORK", "Nasdaq futures -1.6% pre-bell", "24/7 Wall St", "Americas"),
    (30, "WASHINGTON", "Democrats query law firm's free work", "Al Jazeera", "Americas"),
    (31, "WELLINGTON", "Nicholls 175* in a stand of 216", "ICC", "Oceania"),
    (32, "SYDNEY", "Australian shares fall 1.6%", "Reuters", "Oceania"),
    (33, "ANTALYA", "Panama urges a cap on world oil output", "Anadolu", "Global"),
    (34, "ANTALYA", "EU official: climate draft unacceptable", "RTE", "Global"),
    (35, "TURIN", "ATP backs pay plan past $350m", "Anadolu", "Global"),
]

STATS = [
    ("3", "bridges over the Dnipro damaged in Kyiv"),
    ("300,000+", "people moved to shelters before Akvan"),
    ("-6.2%", "Taiwan's share index at Friday's close"),
    ("100,000", "youth visas a year in the UK-EU deal"),
    ("2.3%", "Japan's consumer inflation in October"),
    ("118", "runs by Glenn Phillips against India"),
]

# story number -> (lon, lat) for the map pins
PINS = {
    1: (31, 50), 2: (85, 20), 3: (121, 25), 4: (4, 51), 5: (31, 37),
    6: (23, 52), 7: (44, 33), 8: (12, 42), 9: (139, 36), 10: (127, 38),
    11: (36, 3), 12: (-77, 39), 13: (175, -41), 14: (24, 50), 15: (38, 56),
    16: (13, 53), 17: (0, 52), 18: (116, 40), 19: (141, 34), 20: (129, 36),
    21: (85, 17), 22: (36, 34), 23: (43, 13), 24: (8, 9), 25: (33, 0),
    26: (35, -13), 27: (22, 4), 28: (-115, 36), 29: (-74, 41), 30: (-79, 37),
    31: (177, -43), 32: (151, -34), 33: (29, 39), 34: (33, 35), 35: (8, 45),
}


# ---------------------------------------------------------------- artwork
def art_kyiv(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(38, 44, 66))
    # city silhouette
    for bx, bh in [(x0 + 8, 26), (x0 + 42, 38), (x0 + 84, 22), (x1 - 96, 34),
                   (x1 - 58, 24), (x1 - 34, 40)]:
        d.rectangle([bx, y1 - 34 - bh, bx + 24, y1 - 34], fill=(16, 18, 28))
    # missile streaks
    for sx, sy, ex, ey in [(x0 + 40, y0 + 8, x0 + 120, y0 + 46),
                           (x0 + 150, y0 + 4, x0 + 205, y0 + 40),
                           (x1 - 60, y0 + 10, x1 - 120, y0 + 48)]:
        d.line([sx, sy, ex, ey], fill=(255, 176, 92), width=3)
        d.ellipse([ex - 4, ey - 4, ex + 4, ey + 4], fill=(255, 214, 130))
    # explosion star
    cx, cy = x0 + 128, y0 + 52
    for dx, dy in [(0, -13), (9, -9), (13, 0), (9, 9), (0, 13), (-9, 9),
                   (-13, 0), (-9, -9)]:
        d.line([cx, cy, cx + dx, cy + dy], fill=(255, 120, 60), width=3)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 190, 90))
    # river
    d.rectangle([x0, y1 - 30, x1, y1], fill=(30, 62, 96))
    for wx in range(x0 + 14, x1 - 20, 46):
        d.line([wx, y1 - 15, wx + 22, y1 - 15], fill=(90, 140, 180), width=2)
    # bridge deck + towers + cables
    dy = y1 - 30
    d.line([x0 + 4, dy - 16, x1 - 4, dy - 16], fill=(210, 200, 180), width=4)
    d.line([x0 + 4, dy - 6, x1 - 4, dy - 6], fill=(150, 142, 130), width=2)
    for tx in (x0 + 70, x1 - 70):
        d.line([tx, dy - 44, tx, dy], fill=(210, 200, 180), width=4)
        d.line([tx, dy - 44, x0 + 6, dy - 16], fill=(170, 162, 148), width=2)
        d.line([tx, dy - 44, x1 - 6, dy - 16], fill=(170, 162, 148), width=2)


def art_cyclone(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(96, 164, 188))
    cx, cy = x0 + (x1 - x0) * 0.36, y0 + (y1 - y0) * 0.44
    # spiral arms
    for r, a0 in [(16, 20), (26, 130), (36, 240), (46, 350), (56, 100),
                  (66, 210), (76, 320)]:
        d.arc([cx - r, cy - r * 0.72, cx + r, cy + r * 0.72],
              start=a0, end=a0 + 150, fill=WHITE, width=5)
    d.ellipse([cx - 8, cy - 6, cx + 8, cy + 6], fill=(30, 90, 120))
    # coast + sea
    d.polygon([(x1 - 88, y0), (x1, y0), (x1, y1), (x1 - 40, y1),
               (x1 - 58, y1 - 40), (x1 - 96, y1 - 62)], fill=(226, 205, 150))
    d.rectangle([x0, y1 - 26, x1 - 44, y1], fill=(36, 110, 150))
    for wx in range(x0 + 8, x1 - 60, 40):
        d.arc([wx, y1 - 22, wx + 26, y1 - 6], 180, 360,
              fill=(170, 220, 240), width=2)
    # bent palm
    px, py = x1 - 66, y1 - 8
    d.line([px, py, px - 6, py - 30, px - 18, py - 44], fill=(90, 70, 40), width=4)
    for dx, dy in [(-26, -52), (-12, -56), (2, -54), (-20, -44)]:
        d.line([px - 18, py - 44, px - 18 + dx, py - 44 + dy + 48],
               fill=(46, 120, 60), width=3)
    # rain
    for i in range(9):
        rx = x0 + 18 + i * 30
        d.line([rx, y0 + 12, rx - 6, y0 + 26], fill=(220, 240, 250), width=2)


def art_markets(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(24, 28, 44))
    for gy in range(y0 + 14, y1 - 10, 18):
        d.line([x0 + 8, gy, x1 - 8, gy], fill=(52, 60, 84), width=1)
    # falling bars
    bars = [(0.82, 26), (0.70, 34), (0.74, 30), (0.52, 44), (0.40, 52),
            (0.24, 62)]
    bw = (x1 - x0 - 40) // len(bars)
    for i, (top, _) in enumerate(bars):
        bx = x0 + 16 + i * bw
        by = y0 + 12 + int((y1 - y0 - 34) * (1 - top))
        d.rectangle([bx, by, bx + bw - 8, y1 - 12], fill=(70, 90, 140))
    pts = [(x0 + 24, y0 + 22), (x0 + 70, y0 + 34), (x0 + 118, y0 + 30),
           (x0 + 166, y0 + 52), (x0 + 214, y0 + 64), (x0 + 262, y0 + 84),
           (x1 - 14, y0 + 92)]
    pts = [(px, min(py, y1 - 16)) for px, py in pts]
    d.line(pts, fill=(255, 84, 84), width=4)
    for px, py in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 150, 150))
    ax, ay = pts[-1]
    d.polygon([(ax, ay), (ax - 16, ay - 4), (ax - 6, ay + 12)],
              fill=(255, 84, 84))


def art_eu(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(36, 66, 140))
    import math
    cx, cy = (x0 + x1) // 2 - 34, (y0 + y1) // 2
    for i in range(12):
        a = math.radians(i * 30 - 90)
        sx, sy = cx + 20 * math.cos(a), cy + 20 * math.sin(a)
        d.polygon([(sx, sy - 4), (sx + 3, sy + 3), (sx - 3, sy + 3)],
                  fill=(250, 205, 60))
    # UK flag suggestion: white/red cross panel
    fx = (x0 + x1) // 2 + 12
    d.rectangle([fx, cy - 22, fx + 52, cy + 22], fill=(30, 50, 120))
    d.rectangle([fx, cy - 5, fx + 52, cy + 5], fill=WHITE)
    d.rectangle([fx + 21, cy - 22, fx + 31, cy + 22], fill=WHITE)
    d.rectangle([fx, cy - 3, fx + 52, cy + 3], fill=(200, 40, 50))
    d.rectangle([fx + 23, cy - 22, fx + 29, cy + 22], fill=(200, 40, 50))
    d.line([x0 + 10, y1 - 6, x1 - 10, y1 - 6], fill=(250, 205, 60), width=3)


def art_cop(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(214, 232, 240))
    cx, cy = (x0 + x1) // 2 - 16, (y0 + y1) // 2
    r = min(x1 - x0, y1 - y0) // 2 - 6
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(64, 140, 190))
    d.ellipse([cx - r // 2, cy - r, cx, cy + r], outline=(30, 100, 140), width=2)
    d.ellipse([cx, cy - r, cx + r // 2, cy + r], outline=(30, 100, 140), width=2)
    d.line([cx - r, cy, cx + r, cy], fill=(30, 100, 140), width=2)
    d.polygon([(cx - r + 6, cy - r + 8), (cx - r + 22, cy - r + 4),
               (cx - r + 20, cy - r + 18), (cx - r + 8, cy - r + 16)],
              fill=(80, 160, 90))
    d.polygon([(cx + 4, cy + 6), (cx + 20, cy + 2), (cx + 22, cy + 16),
               (cx + 8, cy + 18)], fill=(80, 160, 90))
    # thermometer
    tx = cx + r + 8
    d.rectangle([tx, cy - r + 4, tx + 7, cy + r - 10], fill=WHITE,
                outline=(150, 40, 40), width=2)
    d.rectangle([tx + 2, cy - 2, tx + 5, cy + r - 10], fill=(210, 50, 50))
    d.ellipse([tx - 3, cy + r - 18, tx + 10, cy + r - 5], fill=(210, 50, 50))


def art_poland(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(150, 190, 110))
    d.rectangle([x0, y1 - 18, x1, y1], fill=(120, 165, 84))
    d.rectangle([x0, y0, x1, y0 + 16], fill=(190, 215, 235))
    # missile in the field
    d.polygon([(x0 + 40, y1 - 26), (x0 + 78, y1 - 52), (x0 + 88, y1 - 44),
               (x0 + 52, y1 - 18)], fill=(120, 120, 128))
    d.polygon([(x0 + 78, y1 - 52), (x0 + 96, y1 - 58), (x0 + 88, y1 - 44)],
              fill=(90, 90, 100))
    d.polygon([(x0 + 40, y1 - 26), (x0 + 30, y1 - 14), (x0 + 46, y1 - 14)],
              fill=(179, 32, 42))
    # flag pole PL
    px = x1 - 34
    d.line([px, y0 + 10, px, y1 - 20], fill=(70, 60, 50), width=3)
    d.rectangle([px, y0 + 10, px + 26, y0 + 19], fill=WHITE)
    d.rectangle([px, y0 + 19, px + 26, y0 + 28], fill=(200, 40, 60))


def art_iraq(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(226, 200, 150))
    d.polygon([(x0, y1), (x0 + 50, y1 - 20), (x0 + 110, y1)], fill=(206, 176, 122))
    d.polygon([(x1 - 90, y1), (x1 - 30, y1 - 16), (x1, y1)], fill=(206, 176, 122))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.polygon([(cx, cy - 22), (cx + 18, cy - 14), (cx + 18, cy + 8),
               (cx, cy + 24), (cx - 18, cy + 8), (cx - 18, cy - 14)],
              outline=(120, 84, 30), width=3)
    import math
    for i in range(5):
        a = math.radians(i * 72 - 90)
        sx, sy = cx + 9 * math.cos(a), cy + 9 * math.sin(a)
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(120, 84, 30))
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(120, 84, 30))
    sx, sy = x0 + 26, y0 + 16
    d.ellipse([sx - 9, sy - 9, sx + 9, sy + 9], fill=(245, 190, 70))


def art_italy(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(206, 216, 226))
    d.rectangle([x0, y1 - 14, x1, y1], fill=(120, 118, 110))
    # placards
    for px, pw, col in [(x0 + 16, 40, (200, 60, 60)), (x0 + 66, 46, (240, 240, 235)),
                        (x0 + 122, 40, (60, 140, 80))]:
        d.line([px + pw // 2, y0 + 30, px + pw // 2, y1 - 22],
               fill=(90, 70, 50), width=3)
        d.rectangle([px, y0 + 6, px + pw, y0 + 30], fill=col,
                    outline=(70, 60, 50), width=1)
    # crowd heads
    for i, hx in enumerate(range(x0 + 14, x1 - 10, 22)):
        hy = y1 - 26 - (i % 2) * 6
        d.ellipse([hx, hy, hx + 13, hy + 13], fill=(60, 52, 46))
        d.rectangle([hx - 1, hy + 12, hx + 14, y1 - 8], fill=(80, 74, 68))


def art_japan(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(244, 240, 232))
    cx, cy = x0 + 34, y0 + 26
    d.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], fill=(205, 45, 55))
    # price tag
    tx0, ty0, tx1, ty1 = x0 + 62, y0 + 12, x1 - 14, y1 - 12
    d.polygon([(tx0 + 12, ty0), (tx1, ty0), (tx1, ty1), (tx0 + 12, ty1),
               (tx0, (ty0 + ty1) // 2)], fill=(250, 205, 60),
              outline=(150, 110, 20), width=2)
    d.ellipse([tx0 + 8, (ty0 + ty1) // 2 - 4, tx0 + 16, (ty0 + ty1) // 2 + 4],
              fill=(244, 240, 232))
    f = F(SANS_B, 17)
    d.text((tx0 + 26, (ty0 + ty1) // 2 - 11), "2.3%", font=f, fill=(90, 60, 10))


def art_korea(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(232, 226, 240))
    cx = (x0 + x1) // 2
    d.line([cx, y0 + 8, cx, y1 - 10], fill=(90, 70, 30), width=4)
    d.line([cx - 34, y0 + 16, cx + 34, y0 + 16], fill=(90, 70, 30), width=4)
    for sgn in (-1, 1):
        px = cx + sgn * 34
        d.line([px, y0 + 16, px - 10, y0 + 36], fill=(90, 70, 30), width=2)
        d.line([px, y0 + 16, px + 10, y0 + 36], fill=(90, 70, 30), width=2)
        d.arc([px - 13, y0 + 30, px + 13, y0 + 46], 0, 180,
              fill=(90, 70, 30), width=3)
    d.rectangle([cx - 16, y1 - 12, cx + 16, y1 - 6], fill=(90, 70, 30))
    d.ellipse([cx - 5, y0 + 3, cx + 5, y0 + 13], fill=(179, 32, 42))


def art_kenya(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(240, 214, 160))
    d.rectangle([x0, y1 - 14, x1, y1], fill=(196, 150, 92))
    cx = (x0 + x1) // 2
    top, bot = y0 + 8, y1 - 14
    d.line([cx - 26, bot, cx, top], fill=(70, 60, 50), width=3)
    d.line([cx + 26, bot, cx, top], fill=(70, 60, 50), width=3)
    d.line([cx - 26, bot, cx + 26, bot], fill=(70, 60, 50), width=3)
    for t in (0.33, 0.66):
        ya = bot + (top - bot) * t
        half = 26 * (1 - t)
        d.line([cx - half, ya, cx + half, ya], fill=(70, 60, 50), width=2)
        d.line([cx - half, ya, cx + half, ya - 12], fill=(70, 60, 50), width=1)
    d.line([cx, top, cx + 30, top + 4], fill=(70, 60, 50), width=3)
    d.line([cx + 30, top + 4, cx + 30, top + 18], fill=(70, 60, 50), width=2)
    d.ellipse([x0 + 12, y0 + 8, x0 + 30, y0 + 26], fill=(245, 170, 60))


def art_trade(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(226, 232, 220))
    dx0, dy0, dx1, dy1 = x0 + 34, y0 + 6, x1 - 34, y1 - 6
    d.rectangle([dx0, dy0, dx1, dy1], fill=(250, 248, 240),
                outline=(110, 105, 90), width=2)
    for i in range(3):
        ly = dy0 + 10 + i * 9
        d.line([dx0 + 10, ly, dx1 - 10, ly], fill=(170, 165, 150), width=2)
    d.ellipse([dx1 - 30, dy1 - 24, dx1 - 12, dy1 - 6], fill=(179, 32, 42))
    d.ellipse([dx1 - 26, dy1 - 20, dx1 - 16, dy1 - 10], outline=WHITE, width=2)
    f = F(SANS_B, 11)
    d.text((dx0 + 10, dy1 - 20), "DEAL", font=f, fill=(90, 85, 70))


def art_cricket(d, b):
    x0, y0, x1, y1 = b
    d.rectangle(b, fill=(120, 175, 95))
    d.rectangle([x0, y1 - 16, x1, y1], fill=(104, 158, 82))
    # stumps
    for sx in (x1 - 44, x1 - 36, x1 - 28):
        d.line([sx, y0 + 18, sx, y1 - 16], fill=(240, 220, 170), width=3)
    # bat
    d.polygon([(x0 + 26, y1 - 10), (x0 + 44, y1 - 12), (x0 + 66, y0 + 22),
               (x0 + 52, y0 + 16)], fill=(232, 205, 160),
              outline=(150, 120, 80), width=2)
    d.line([x0 + 60, y0 + 19, x0 + 74, y0 + 8], fill=(90, 70, 50), width=5)
    # ball
    bx, by = x0 + 88, y0 + 30
    d.ellipse([bx - 10, by - 10, bx + 10, by + 10], fill=(185, 35, 45))
    d.arc([bx - 6, by - 8, bx + 2, by + 8], 270, 90, fill=WHITE, width=2)
    d.arc([bx - 2, by - 8, bx + 6, by + 8], 90, 270, fill=WHITE, width=2)


ART = {"kyiv": art_kyiv, "cyclone": art_cyclone, "markets": art_markets,
       "eu": art_eu, "cop": art_cop, "poland": art_poland, "iraq": art_iraq,
       "italy": art_italy, "japan": art_japan, "korea": art_korea,
       "kenya": art_kenya, "trade": art_trade, "cricket": art_cricket}

# ------------------------------------------------------------- world map
CONTINENTS = [
    # North America
    [(-168, 66), (-150, 70), (-135, 69), (-125, 71), (-110, 68), (-95, 69),
     (-88, 66), (-82, 66), (-80, 62), (-78, 58), (-72, 56), (-65, 50),
     (-70, 44), (-74, 40), (-76, 36), (-80, 32), (-81, 26), (-84, 29),
     (-88, 29), (-93, 29), (-97, 26), (-102, 23), (-106, 22), (-110, 24),
     (-113, 29), (-118, 33), (-122, 37), (-124, 43), (-126, 49), (-132, 55),
     (-148, 60), (-160, 58)],
    # Greenland
    [(-46, 60), (-38, 64), (-30, 68), (-22, 70), (-20, 76), (-28, 81),
     (-48, 80), (-56, 76), (-56, 70), (-52, 63)],
    # South America
    [(-79, 9), (-72, 12), (-64, 10), (-55, 6), (-51, 3), (-50, -1),
     (-44, -3), (-37, -6), (-35, -9), (-39, -14), (-40, -21), (-46, -25),
     (-50, -30), (-54, -35), (-58, -39), (-62, -41), (-65, -45), (-66, -50),
     (-68, -54), (-71, -54), (-73, -50), (-74, -45), (-73, -38), (-71, -30),
     (-70, -21), (-74, -16), (-78, -9), (-81, -5), (-80, 0), (-78, 4)],
    # Europe
    [(-9, 43), (-2, 44), (-1, 46), (-5, 48), (0, 50), (3, 52), (5, 53),
     (8, 54), (8, 57), (12, 56), (18, 56), (21, 58), (24, 59), (28, 60),
     (30, 62), (30, 66), (32, 70), (45, 68), (55, 68), (68, 69), (60, 64),
     (50, 60), (40, 56), (38, 52), (34, 50), (30, 50), (28, 46), (30, 44),
     (28, 41), (26, 40), (23, 37), (22, 37), (24, 40), (20, 42), (16, 40),
     (18, 39), (16, 38), (12, 42), (8, 44), (3, 43), (0, 39), (-2, 37),
     (-6, 36), (-9, 37), (-9, 43)],
    # Africa
    [(-6, 35), (0, 36), (10, 37), (11, 34), (20, 32), (30, 31), (33, 28),
     (35, 24), (37, 20), (39, 15), (43, 12), (48, 11), (51, 12), (46, 5),
     (42, -2), (40, -8), (40, -15), (38, -20), (35, -26), (32, -29),
     (26, -33), (20, -35), (18, -32), (16, -28), (14, -22), (13, -15),
     (12, -8), (10, -2), (9, 4), (4, 6), (-4, 5), (-8, 5), (-13, 8),
     (-16, 12), (-17, 16), (-16, 21), (-13, 28), (-9, 31)],
    # Asia (incl. Siberia, Arabia, India, SE Asia)
    [(30, 50), (34, 50), (38, 52), (40, 56), (50, 60), (60, 64), (68, 69),
     (80, 70), (100, 72), (120, 72), (140, 72), (160, 70), (178, 68),
     (178, 65), (165, 60), (156, 52), (150, 50), (142, 46), (140, 40),
     (135, 35), (129, 33), (122, 30), (120, 25), (114, 22), (108, 16),
     (106, 9), (103, 2), (100, 8), (98, 14), (94, 17), (92, 16), (89, 22),
     (86, 20), (80, 14), (78, 8), (74, 12), (72, 19), (70, 22), (66, 25),
     (61, 25), (57, 26), (52, 26), (50, 29), (48, 30), (44, 29), (43, 12),
     (45, 12), (50, 15), (55, 17), (58, 20), (59, 22), (55, 24), (51, 24),
     (50, 26), (48, 28), (44, 29), (40, 31), (36, 36), (30, 41), (28, 41),
     (30, 46)],
    # Indonesia / Papua blobs
    [(95, 5), (102, -2), (108, -5), (114, -3), (120, -2), (126, -3),
     (132, -4), (138, -3), (144, -5), (148, -8), (142, -8), (134, -6),
     (126, -6), (118, -6), (110, -7), (102, -4), (96, 2)],
    # Australia
    [(113, -22), (114, -28), (115, -33), (118, -35), (124, -33), (130, -32),
     (134, -33), (137, -35), (140, -38), (145, -38), (150, -37), (153, -31),
     (153, -27), (151, -24), (149, -20), (146, -19), (143, -15), (142, -11),
     (140, -13), (139, -17), (136, -15), (135, -12), (132, -11), (129, -14),
     (126, -14), (122, -17), (118, -20), (114, -21)],
]


def draw_map(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(196, 218, 232))
    w_, h_ = x1 - x0, y1 - y0

    def px(lon, lat):
        # latitude cropped to 85..-58 so the inhabited world gets more room
        return (x0 + (lon + 180) / 360.0 * w_,
                y0 + (85 - lat) / 143.0 * h_)

    land = (150, 178, 128)
    for poly in CONTINENTS:
        d.polygon([px(lon, lat) for lon, lat in poly], fill=land)
    # UK, Japan, NZ marks
    for lon, lat, r in [(-2, 53, 3), (138, 37, 4), (172, -42, 3),
                        (127, 37, 3), (121, 24, 2)]:
        cx, cy = px(lon, lat)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=land)
    for num, (lon, lat) in PINS.items():
        cx, cy = px(lon, lat)
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=RED,
                  outline=WHITE, width=1)
        f = F(SANS_B, 8)
        s = str(num)
        d.text((cx - tw(d, s, f) / 2, cy - 4), s, font=f, fill=WHITE)


# ---------------------------------------------------------------- layout
MX = 28            # side margin
CW = W - 2 * MX    # content width = 968


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- kicker
    d.text((MX, 14), "THE WORLD IN ONE DAY", font=F(SANS_B, 16), fill=RED)
    kr = "35 STORIES - 7 REGIONS - EVERY ONE DATED FRIDAY 20 NOVEMBER 2026"
    kf = fit_font(d, kr, SANS_B, 13, 9, CW - 240)
    d.text((W - MX - tw(d, kr, kf), 16), kr, font=kf, fill=RED)
    d.line([MX, 40, W - MX, 40], fill=RULE, width=1)
    d.line([MX, 44, W - MX, 44], fill=RULE, width=3)

    # ---- masthead
    mast = "Friday 20 November 2026"
    mf = fit_font(d, mast, SERIF_B, 78, 40, CW)
    mw = tw(d, mast, mf)
    d.text(((W - mw) / 2, 50), mast, font=mf, fill=INK)
    deck = ("Missiles hit Kyiv's bridges - Cyclone Akvan ashore in Odisha - "
            "Asia's markets sink in an AI rout - UK and EU seal a reset deal")
    df = fit_font(d, deck, SANS, 16, 10, CW)
    dw = tw(d, deck, df)
    d.text(((W - dw) / 2, 128), deck, font=df, fill=(60, 54, 44))
    d.line([MX, 152, W - MX, 152], fill=RULE, width=1)

    # ---- stat strip
    sy = 160
    sw = CW / 6.0
    for i, (num, cap) in enumerate(STATS):
        cx = MX + i * sw + sw / 2
        nf = F(SERIF_B, 27)
        d.text((cx - tw(d, num, nf) / 2, sy), num, font=nf, fill=DARKRED)
        cf = F(SANS, 10)
        for j, ln in enumerate(wrap(d, cap, cf, sw - 14)):
            d.text((cx - tw(d, ln, cf) / 2, sy + 34 + j * 12), ln,
                   font=cf, fill=GREY)
        if i:
            d.line([MX + i * sw, sy + 4, MX + i * sw, sy + 52],
                   fill=(200, 192, 172), width=1)
    d.line([MX, 218, W - MX, 218], fill=RULE, width=1)

    # ---- region bar
    ry, rh = 226, 27
    x = MX
    total = sum(c for _, c in REGIONS)
    for name, count in REGIONS:
        segw = CW * count / total
        col = REGION_COLORS[{"EUROPE": "Europe", "ASIA": "Asia",
                             "MIDDLE EAST": "Middle East", "AFRICA": "Africa",
                             "AMERICAS": "Americas", "OCEANIA": "Oceania",
                             "GLOBAL": "Global"}[name]]
        d.rectangle([x, ry, x + segw - 2, ry + rh], fill=col)
        label = "%s %d" % (name, count)
        lf = fit_font(d, label, SANS_B, 12, 8, segw - 8)
        d.text((x + (segw - 2 - tw(d, label, lf)) / 2,
                ry + (rh - lf.size) / 2 - 1), label, font=lf, fill=WHITE)
        x += segw

    # ---- heroes
    hy, hh = 266, 216
    hw, hgap = 314, 13
    for i, s in enumerate(HEROES):
        x = MX + i * (hw + hgap)
        box = (x, hy, x + hw, hy + 102)
        ART[s["art"]](d, box)
        d.rectangle(box, outline=RULE, width=1)
        source_tag(d, box, s["src"])
        badge(d, x + 16, hy + 16, 13, s["num"])
        d.text((x, hy + 108), s["tag"], font=F(SANS_B, 11),
               fill=REGION_COLORS[s["region"]])
        text_block(d, x, hy + 124, s["head"], F(SERIF_B, 17), hw, 21,
                   max_lines=2)
        text_block(d, x, hy + 168, s["body"], F(SANS, 12), hw, 15,
                   max_lines=3)

    # ---- briefs (two rows of five)
    bw_, bgap = 186, 9
    for r in range(2):
        by = 490 + r * 128
        for c in range(5):
            s = BRIEFS[r * 5 + c]
            x = MX + c * (bw_ + bgap)
            box = (x, by, x + bw_, by + 54)
            ART[s["art"]](d, box)
            d.rectangle(box, outline=RULE, width=1)
            source_tag(d, box, s["src"])
            badge(d, x + 12, by + 12, 10, s["num"])
            text_block(d, x, by + 59, s["head"], F(SANS_B, 12), bw_, 14,
                       max_lines=2)
            text_block(d, x, by + 89, s["body"], F(SANS, 10), bw_, 12,
                       max_lines=3)

    # ---- map + date check row
    my = 750
    d.text((MX, my), "WHERE IT HAPPENED", font=F(SANS_B, 12), fill=INK)
    draw_map(d, (MX, my + 18, MX + 520, my + 106))
    d.rectangle([MX, my + 18, MX + 520, my + 106], outline=RULE, width=1)
    dx0, dx1 = MX + 536, W - MX
    d.rectangle([dx0, my, dx1, my + 106], outline=RED, width=2)
    d.text((dx0 + 10, my + 7), "DATE CHECK", font=F(SANS_B, 12), fill=RED)
    dctext = ("Left out, as Thursday 19 November's news: the World Court's "
              "ruling on Myanmar, the three-leader declaration in Shenzhen, "
              "Tonga's drought emergency and the migrant boat lost off "
              "Senegal. Not yet happened, so not shown: BepiColombo's entry "
              "into orbit round Mercury, and any final COP31 text.")
    text_block(d, dx0 + 10, my + 26, dctext, F(SANS, 10), dx1 - dx0 - 20, 13)

    # ---- index
    iy = 866
    ih = "ALSO ON FRIDAY 20 NOVEMBER - 22 MORE STORIES"
    d.text((MX, iy), ih, font=F(SANS_B, 13), fill=INK)
    d.line([MX, iy + 18, W - MX, iy + 18], fill=RULE, width=1)
    cols = [(MX, 316), (MX + 328, 316), (MX + 656, 312)]
    per = 8
    for ci, (cx, cw) in enumerate(cols):
        for ri in range(per):
            idx = ci * per + ri
            if idx >= len(INDEX):
                break
            num, place, fact, src, region = INDEX[idx]
            line = "%d  %s - %s - %s" % (num, place, fact, src)
            lf = fit_font(d, line, SANS, 10, 8, cw)
            d.text((cx, iy + 24 + ri * 11.5), line, font=lf, fill=INK)

    # ---- footer
    foot = ("Every story on this page happened, or was first reported, on "
            "Friday 20 November 2026. Figures given by officials are reported "
            "as stated and attributed; a source is named beside each story. "
            "All illustrations are original drawings made for this page.")
    ff = F(SANS, 9)
    fy = 990
    for ln in wrap(d, foot, ff, CW):
        d.text(((W - tw(d, ln, ff)) / 2, fy), ln, font=ff, fill=GREY)
        fy += 11

    return img


def main():
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img = render()
    img.save(out, format="PNG", optimize=True)
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()
