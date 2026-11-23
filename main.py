#!/usr/bin/env python3
"""News poster for Monday 23 November 2026.

Draws a one-page newspaper front page summing up the day's world news.
Pure Python 3.13 standard library: the PNG bytes are encoded by hand
(zlib + CRC32) and every letter comes from a small 5x7 dot font defined
below. No network, no randomness, no clock: two runs write identical bytes.

Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py   -> out/entry.png
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)
INK = (18, 28, 48)
NAVY = (16, 32, 66)
RED = (178, 35, 27)
GOLD = (214, 164, 32)
TEAL = (14, 110, 105)
SLATE = (88, 96, 110)
LIGHT = (233, 227, 210)
WHITE = (255, 255, 255)
SKY = (141, 190, 214)
GREEN = (46, 125, 50)

# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 bits, written as strings of '#' / '.'.
_FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '*': ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
}
_BLANK = ("00000",) * 7


def text_width(text, scale):
    """Pixel width of text at the given scale (6 units per glyph)."""
    return len(text) * 6 * scale - scale


def wrap(text, max_chars):
    """Greedy word wrap into lines of at most max_chars characters."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg) * (w * h)

    def _set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def hline(self, x, y, length, color, thick=1):
        self.rect(x, y, length, thick, color)

    def vline(self, x, y, length, color, thick=1):
        self.rect(x, y, thick, length, color)

    def disc(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def ring(self, cx, cy, r, color, thick=2):
        for t in range(thick):
            rr = r - t
            for dy in range(-rr, rr + 1):
                dx = int((rr * rr - dy * dy) ** 0.5)
                self._set(cx - dx, cy + dy, color)
                self._set(cx + dx, cy + dy, color)

    def triangle(self, ax, ay, bx, by, cx, cy, color):
        """Filled triangle via scanline interpolation."""
        pts = sorted(((ax, ay), (bx, by), (cx, cy)), key=lambda p: p[1])
        (x0, y0), (x1, y1), (x2, y2) = pts
        if y0 == y2:
            return
        def edge_x(xa, ya, xb, yb, y):
            if yb == ya:
                return xa
            return xa + (xb - xa) * (y - ya) / (yb - ya)
        for y in range(max(0, y0), min(self.h, y2 + 1)):
            if y < y1:
                xa = edge_x(x0, y0, x1, y1, y)
                xb = edge_x(x0, y0, x2, y2, y)
            else:
                xa = edge_x(x1, y1, x2, y2, y)
                xb = edge_x(x0, y0, x2, y2, y)
            lo, hi = sorted((int(xa), int(xb)))
            self.rect(lo, y, hi - lo + 1, 1, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        steps = max(dx, dy, 1)
        for s in range(steps + 1):
            x = x0 + (x1 - x0) * s // steps
            y = y0 + (y1 - y0) * s // steps
            self.rect(x - thick // 2, y - thick // 2, thick, thick, color)

    def glyph(self, ch, x, y, scale, color):
        rows = _FONT.get(ch.upper(), _BLANK)
        for r, bits in enumerate(rows):
            for c, bit in enumerate(bits):
                if bit == '1':
                    self.rect(x + c * scale, y + r * scale, scale, scale, color)

    def text(self, s, x, y, scale, color):
        for ch in s:
            self.glyph(ch, x, y, scale, color)
            x += 6 * scale
        return x

    def centred(self, s, cx, y, scale, color):
        self.text(s, cx - text_width(s, scale) // 2, y, scale, color)

    def para(self, s, x, y, max_chars, scale, color, leading=None):
        """Wrapped paragraph; returns y just below the last line."""
        lh = leading if leading is not None else 9 * scale
        for line in wrap(s, max_chars):
            self.text(line, x, y, scale, color)
            y += lh
        return y


# ---------------------------------------------------------------- PNG encode
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def encode_png(cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + _chunk(b"IEND", b""))


# ---------------------------------------------------------------- pictures
def draw_globe(cv, cx, cy, r):
    """A warming globe: blue disc, green land blobs, red crack, sun rays."""
    cv.disc(cx, cy, r, SKY)
    cv.ring(cx, cy, r, NAVY, 3)
    # land blobs (simple rounded shapes)
    cv.disc(cx - r // 3, cy - r // 4, r // 3, GREEN)
    cv.disc(cx + r // 4, cy + r // 5, r // 4, GREEN)
    cv.disc(cx + r // 5, cy - r // 2, r // 5, GREEN)
    cv.disc(cx - r // 2, cy + r // 3, r // 5, GREEN)
    # crack across the globe
    cv.line(cx - r + 8, cy + r // 4, cx - r // 4, cy - r // 6, RED, 4)
    cv.line(cx - r // 4, cy - r // 6, cx + r // 3, cy + r // 3, RED, 4)
    cv.line(cx + r // 3, cy + r // 3, cx + r - 6, cy - r // 5, RED, 4)
    # heat rays above
    for dx in (-r - 18, -r // 2 - 14, 0, r // 2 + 14, r + 18):
        cv.line(cx + dx, cy - r - 26, cx + dx, cy - r - 10, RED, 4)


def draw_burst(cv, cx, cy, r, color):
    """Explosion starburst for the Kyiv strike."""
    for k in range(12):
        ang = k * 30
        import math
        x2 = cx + int(r * math.cos(math.radians(ang)))
        y2 = cy + int(r * math.sin(math.radians(ang)))
        cv.line(cx, cy, x2, y2, color, 3)
    cv.disc(cx, cy, r // 3, color)


def draw_flame(cv, cx, cy, s):
    cv.triangle(cx, cy - 3 * s, cx - 2 * s, cy + 2 * s, cx + 2 * s, cy + 2 * s, RED)
    cv.triangle(cx, cy - s, cx - s, cy + 2 * s, cx + s, cy + 2 * s, GOLD)
    cv.disc(cx, cy + 2 * s, s // 2, GOLD)


def draw_ship(cv, cx, cy, s):
    cv.triangle(cx - 3 * s, cy, cx + 3 * s, cy, cx + 2 * s, cy + 2 * s, NAVY)
    cv.rect(cx - 3 * s, cy, 6 * s, s, NAVY)
    cv.rect(cx - s, cy - 2 * s, 2 * s, 2 * s, RED)
    cv.line(cx - 4 * s, cy + 3 * s, cx + 4 * s, cy + 3 * s, TEAL, 2)
    cv.line(cx - 3 * s, cy + 4 * s, cx + 3 * s, cy + 4 * s, TEAL, 2)


def draw_chip(cv, cx, cy, s):
    cv.rect(cx - 2 * s, cy - 2 * s, 4 * s, 4 * s, NAVY)
    cv.rect(cx - s, cy - s, 2 * s, 2 * s, GOLD)
    for dx in (-2, 0, 2):
        cv.line(cx + dx * s, cy - 3 * s, cx + dx * s, cy - 2 * s, NAVY, 2)
        cv.line(cx + dx * s, cy + 2 * s, cx + dx * s, cy + 3 * s, NAVY, 2)
        cv.line(cx - 3 * s, cy + dx * s, cx - 2 * s, cy + dx * s, NAVY, 2)
        cv.line(cx + 2 * s, cy + dx * s, cx + 3 * s, cy + dx * s, NAVY, 2)


def draw_cap(cv, cx, cy, s):
    cv.triangle(cx - 3 * s, cy, cx, cy - 2 * s, cx + 3 * s, cy, NAVY)
    cv.rect(cx - 2 * s, cy, 4 * s, 2 * s, NAVY)
    cv.line(cx + 3 * s, cy - s, cx + 3 * s, cy + 2 * s, GOLD, 2)
    cv.disc(cx + 3 * s, cy + 2 * s, s // 2, GOLD)


def draw_chess(cv, cx, cy, s):
    for r in range(4):
        for c in range(4):
            if (r + c) % 2 == 0:
                cv.rect(cx - 2 * s + c * s, cy - 2 * s + r * s, s, s, INK)
    cv.disc(cx + s, cy - s, s, WHITE)
    cv.rect(cx, cy - 2 * s, 2 * s, s, WHITE)


def draw_bat(cv, cx, cy, s):
    cv.line(cx - 2 * s, cy + 3 * s, cx + 2 * s, cy - 3 * s, (139, 90, 43), 4)
    cv.disc(cx + 3 * s, cy - 3 * s, s, RED)


# ---------------------------------------------------------------- layout
def build():
    cv = Canvas(W, H, PAPER)

    # ---- masthead
    cv.rect(0, 0, W, 118, NAVY)
    cv.centred("THE WORLD IN ONE DAY", W // 2, 16, 5, WHITE)
    cv.centred("MONDAY  *  23 NOVEMBER 2026", W // 2, 76, 3, GOLD)
    cv.hline(0, 118, W, RED, 6)

    # ---- lead story: COP31 collapse
    lead_y = 140
    cv.text("CLIMATE  -  ANTALYA, TURKIYE", 36, lead_y, 2, RED)
    cv.text("COP31 COLLAPSES", 36, lead_y + 28, 6, INK)
    cv.text("NO DEAL ON FOSSIL FUELS", 36, lead_y + 76, 3, INK)
    cv.para("The UN climate summit ends with no agreement - the first "
            "collapse since 2009 and the longest COP on record. The EU "
            "and island states reject a draft that never names fossil "
            "fuels; Australia's PM calls it a sign of difficult times.",
            36, lead_y + 118, 52, 2, SLATE)
    draw_globe(cv, 880, lead_y + 105, 78)

    cv.hline(36, 372, W - 72, INK, 2)

    # ---- story grid: 2 columns x 3 rows
    cards = [
        ("UKRAINE", "DRONE HITS KYIV FLATS", RED,
         "A Russian drone strike on a building in the Kyiv region "
         "leaves at least 14 people missing. Zelenskyy presses the "
         "US for Patriot missiles as winter attacks mount.",
         lambda cx, cy: draw_burst(cv, cx, cy, 26, RED)),
        ("GULF WAR", "HORMUZ IN FLAMES", TEAL,
         "Houthis claim strikes on a Saudi oil refinery and radar, "
         "with at least six hurt, as tankers are set ablaze in the "
         "Strait of Hormuz and the Iran war widens.",
         lambda cx, cy: draw_flame(cv, cx, cy, 12)),
        ("BLACK SEA", "SEA DRONES HIT WARSHIP", NAVY,
         "Suspected Ukrainian sea drones strike a Russian warship at "
         "the Benghazi naval base in Libya, officials say - the war "
         "at sea reaching the Mediterranean.",
         lambda cx, cy: draw_ship(cv, cx, cy, 8)),
        ("TECH", "UN TALKS ON KILLER ROBOTS", TEAL,
         "Nations agree at a UN conference to continue negotiations "
         "on lethal autonomous weapons - no ban yet, but talks on "
         "rules for AI in war stay alive.",
         lambda cx, cy: draw_chip(cv, cx, cy, 9)),
        ("ASIA", "MINISTER QUITS OVER AI CHEATING", NAVY,
         "South Korea's education minister resigns amid an AI exam-"
         "cheating scandal, as schools reel from leaked papers and "
         "machine-written answers.",
         lambda cx, cy: draw_cap(cv, cx, cy, 9)),
        ("SPORT", "CHESS CROWN, CRICKET RECORD", RED,
         "The World Chess Championship opens with Sindarov taking "
         "White in Game 1, while India posts a record 720 for 9 "
         "declared in the Wellington Test.",
         lambda cx, cy: (draw_chess(cv, cx - 22, cy, 9),
                          draw_bat(cv, cx + 34, cy, 7))),
    ]
    gx, gy = 36, 392
    cw, chh, gap = 464, 158, 24
    for i, (kicker, head, color, body, icon) in enumerate(cards):
        x = gx + (i % 2) * (cw + gap)
        y = gy + (i // 2) * (chh + 16)
        cv.rect(x, y, cw, chh, WHITE)
        cv.rect(x, y, 6, chh, color)
        cv.text(kicker, x + 20, y + 12, 2, color)
        cv.text(head, x + 20, y + 36, 2, INK)
        cv.para(body, x + 20, y + 66, 36, 2, SLATE)
        icon(x + cw - 52, y + 34)

    # ---- also today strip
    ay = 906
    cv.rect(0, ay, W, 88, NAVY)
    cv.text("ALSO TODAY", 36, ay + 10, 2, GOLD)
    cv.para("Nepal PM Balendra Shah meets Modi in Delhi  -  "
            "Thousands march in Lisbon over living costs  -  "
            "50 missing after an Indonesian factory fire  -  "
            "Myanmar junta calls an ASEAN decision unfair  -  "
            "Father and daughter held by ICE at Seattle airport.",
            36, ay + 34, 80, 2, WHITE, leading=14)

    # ---- footer
    cv.centred("ALL EVENTS FIRST REPORTED ON 23 NOVEMBER 2026",
              W // 2, 1004, 1, SLATE)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    data = encode_png(build())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print(f"wrote {path} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
