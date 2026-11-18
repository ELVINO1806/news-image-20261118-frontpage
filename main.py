#!/usr/bin/env python3
# Front page generator for the news-image-20261118 entry.
"""News front page generator for Wednesday 18 November 2026.

Hand-rolled PNG encoder, RGB pixel canvas, drawing primitives and a
hand-authored 5x7 bitmap font. Python 3.13 standard library only.
Deterministic: no network, no randomness, no clock.
"""
import os
import struct
import sys
import zlib

W = 1024
H = 1024

PAPER = (246, 241, 227)
INK = (20, 18, 14)
RED = (158, 27, 27)
SLATE = (51, 86, 110)
GREY = (110, 108, 100)
LIGHT = (214, 207, 190)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- font
# 5x7 glyphs as string art, authored for this program.
_F = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", ".#.#.", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "a": (".....", ".....", ".####", "....#", ".####", "#...#", ".####"),
    "b": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    "c": (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    "d": ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    "e": (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    "f": ("..##.", ".#...", ".#...", "####.", ".#...", ".#...", ".#..."),
    "g": (".....", ".####", "#...#", "#...#", ".####", "....#", ".###."),
    "h": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "i": ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
    "j": ("...#.", ".....", "..##.", "...#.", "...#.", "#..#.", ".##.."),
    "k": ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    "l": (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "m": (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    "n": (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "o": (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    "p": (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    "q": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    "r": (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    "s": (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    "t": (".#...", ".#...", "####.", ".#...", ".#...", ".#..#", "..##."),
    "u": (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    "v": (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "w": (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "x": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    "y": (".....", ".....", "#...#", "#...#", "#...#", ".####", "....#"),
    "z": (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "\u2013": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "\u00b7": (".....", ".....", ".....", ".##..", ".##..", ".....", "....."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#..##"),
    "(": ("..##.", ".#...", "#....", "#....", "#....", ".#...", "..##."),
    ")": (".##..", "...#.", "....#", "....#", "....#", "...#.", ".##.."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
}
# Curly quotes from word processors map onto the plain glyphs.
_F["\u2019"] = _F["'"]
_F["\u2018"] = _F["'"]
_F["\u201c"] = _F['"']
_F["\u201d"] = _F['"']
_F["\u2014"] = _F["-"]


def _bold_dx(sx):
    return max(1, sx // 3) if sx > 1 else 1


def text_width(text, sx, bold=False, spacing=2):
    if not text:
        return 0
    adv = 5 * sx + spacing + (_bold_dx(sx) if bold else 0)
    return adv * len(text) - spacing


def draw_text(cv, x, y, text, sx, sy, color, bold=False, spacing=2):
    adv = 5 * sx + spacing + (_bold_dx(sx) if bold else 0)
    cx = x
    for ch in text:
        glyph = _F.get(ch, _F["?"])
        for row in range(7):
            line = glyph[row]
            for col in range(5):
                if line[col] == "#":
                    px = cx + col * sx
                    py = y + row * sy
                    cv.rect(px, py, sx, sy, color)
                    if bold:
                        cv.rect(px + _bold_dx(sx), py, sx, sy, color)
        cx += adv
    return cx - spacing


def draw_text_centered(cv, y, text, sx, sy, color, bold=False, spacing=2):
    w = text_width(text, sx, bold, spacing)
    return draw_text(cv, (W - w) // 2, y, text, sx, sy, color, bold, spacing)


def wrap_text(text, max_width, sx, bold=False, spacing=2):
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, sx, bold, spacing) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(cv, x, y, text, max_width, sx, sy, color,
                 bold=False, spacing=2, line_gap=3):
    lines = wrap_text(text, max_width, sx, bold, spacing)
    for line in lines:
        draw_text(cv, x, y, line, sx, sy, color, bold, spacing)
        y += 7 * sy + line_gap
    return y


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = color[0]
            self.buf[i + 1] = color[1]
            self.buf[i + 2] = color[2]

    def rect(self, x, y, rw, rh, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + rw)
        y1 = min(self.h, y + rh)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + len(row)] = row

    def hline(self, x, y, length, color, thick=1):
        self.rect(x, y, length, thick, color)

    def vline(self, x, y, length, color, thick=1):
        self.rect(x, y, thick, length, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for s in range(steps + 1):
            x = x0 + (x1 - x0) * s // steps
            y = y0 + (y1 - y0) * s // steps
            self.rect(x - thick // 2, y - thick // 2, thick, thick, color)

    def circle(self, cx, cy, r, color, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if fill and d <= r * r:
                    self.set(xx, yy, color)
                elif not fill and r * r - 2 * r <= d <= r * r:
                    self.set(xx, yy, color)

    def polygon(self, pts, color):
        ys = [p[1] for p in pts]
        for yy in range(min(ys), max(ys) + 1):
            nodes = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    nodes.append(x0 + (yy - y0) * (x1 - x0) // (y1 - y0))
            nodes.sort()
            for i in range(0, len(nodes) - 1, 2):
                self.hline(nodes[i], yy, nodes[i + 1] - nodes[i] + 1, color)

    def waves(self, x, y, width, color, rows=3, amp=4, period=28, thick=2):
        for r in range(rows):
            yy = y + r * (amp * 2 + 5)
            for xx in range(width):
                off = amp if (xx // (period // 2)) % 2 == 0 else -amp
                # smooth-ish scallop: use a stepped sine approximation
                phase = (xx % period) * 4 // period
                lift = (0, amp // 2, amp, amp // 2)[phase]
                if (xx // (period // 2)) % 2 == 1:
                    lift = amp - lift
                self.rect(x + xx, yy + lift, 1, thick, color)
                _ = off


# ---------------------------------------------------------------- png
def _chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def write_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for yy in range(cv.h):
        raw.append(0)
        raw += cv.buf[yy * stride:(yy + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n"
           + _chunk(b"IHDR", ihdr)
           + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + _chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)
    return len(png)


# ---------------------------------------------------------------- art
def draw_bridge(cv, x, y, w, h):
    deck_y = y + 16
    # drone dots in the sky
    for dx, dy in ((30, 2), (86, 6), (150, 1), (430, 4), (520, 8)):
        cv.rect(x + dx, y + dy, 5, 5, INK)
        cv.rect(x + dx + 2, y + dy - 2, 1, 9, INK)
    # towers
    cv.rect(x + 70, y + 4, 7, 34, INK)
    cv.rect(x + 300, y + 4, 7, 34, INK)
    # suspension cables
    cv.line(x + 4, deck_y, x + 73, y + 5, GREY, 2)
    cv.line(x + 73, y + 5, x + 303, deck_y, GREY, 2)
    cv.line(x + 303, y + 5, x + 420, deck_y, GREY, 2)
    # deck, left intact part and a short right stub
    cv.rect(x, deck_y, 408, 5, INK)
    cv.rect(x + 492, deck_y, w - 492, 5, INK)
    # piers
    cv.rect(x + 70, deck_y + 5, 7, 16, INK)
    cv.rect(x + 300, deck_y + 5, 7, 16, INK)
    cv.rect(x + 540, deck_y + 5, 7, 16, INK)
    # broken arch segment, tilted down into the sea (accent red)
    cv.polygon([(x + 414, deck_y + 2), (x + 486, deck_y + 10),
                (x + 478, deck_y + 22), (x + 408, deck_y + 12)], RED)
    cv.line(x + 420, deck_y + 4, x + 452, deck_y + 26, RED, 3)
    # sea
    cv.waves(x + 2, y + h - 16, w - 4, SLATE, rows=2, amp=3, period=26)


def draw_tanker(cv, x, y, w, h):
    hull_y = y + h - 24
    # hull
    cv.polygon([(x + 20, hull_y), (x + w - 30, hull_y),
                (x + w - 52, hull_y + 13), (x + 44, hull_y + 13)], INK)
    # deck tanks
    for i in range(3):
        cv.rect(x + 52 + i * 62, hull_y - 9, 48, 9, SLATE)
    # superstructure and funnel
    cv.rect(x + w - 92, hull_y - 24, 30, 24, INK)
    cv.rect(x + w - 84, hull_y - 32, 12, 8, INK)
    # mast
    cv.rect(x + 30, hull_y - 26, 3, 26, INK)
    cv.line(x + 31, hull_y - 26, x + 70, hull_y - 6, GREY, 1)
    # flame above the middle tank
    fx = x + 128
    cv.polygon([(fx, hull_y - 34), (fx + 9, hull_y - 18),
                (fx + 4, hull_y - 12), (fx - 5, hull_y - 18)], RED)
    cv.polygon([(fx + 2, hull_y - 24), (fx + 6, hull_y - 17),
                (fx + 2, hull_y - 14), (fx - 2, hull_y - 17)], RED)
    cv.waves(x + 2, y + h - 12, w - 4, SLATE, rows=1, amp=3, period=24)


def draw_icon(cv, x, y, kind):
    s = 18
    if kind == "building":
        cv.polygon([(x + 9, y), (x + s, y + 6), (x, y + 6)], RED)
        for i in range(3):
            cv.rect(x + 2 + i * 6, y + 8, 3, 8, INK)
        cv.rect(x, y + 16, s, 2, INK)
    elif kind == "quad":
        for dy in (0, 10):
            for dx in (0, 10):
                cv.rect(x + dx, y + dy, 8, 8, SLATE)
    elif kind == "sun":
        cv.circle(x + 9, y + 8, 6, RED)
        cv.waves(x, y + 13, s, SLATE, rows=1, amp=2, period=10, thick=2)
    elif kind == "tent":
        cv.polygon([(x + 9, y + 1), (x + s, y + 17), (x, y + 17)], SLATE)
        cv.polygon([(x + 9, y + 9), (x + 13, y + 17), (x + 5, y + 17)], PAPER)
    elif kind == "storm":
        cv.circle(x + 9, y + 9, 8, SLATE, fill=False)
        cv.circle(x + 9, y + 9, 4, SLATE, fill=False)
        cv.rect(x + 8, y + 8, 3, 3, RED)
    elif kind == "cross":
        cv.rect(x + 6, y, 6, s, RED)
        cv.rect(x, y + 6, s, 6, RED)


# ---------------------------------------------------------------- layout
MX = 18
CW = W - 2 * MX  # 988


def panel(cv, x, y, w, icon, headline, body):
    draw_icon(cv, x, y + 4, icon)
    draw_text(cv, x + 26, y, headline, 2, 5, INK, bold=True, spacing=0)
    draw_wrapped(cv, x, y + 42, body, w, 2, 3, INK, spacing=0, line_gap=2)  # panel body text


def draw_brief(cv, x, y, col_w, tag, rest):
    draw_text(cv, x, y, tag, 2, 3, RED, bold=True, spacing=1)
    tag_w = text_width(tag, 2, bold=True, spacing=1)
    first_w = col_w - tag_w - 10
    words = rest.split(" ")
    lines = []
    cur = ""
    limit = first_w
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, 2, spacing=0) <= limit or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
            limit = col_w
    if cur:
        lines.append(cur)
    lx = x + tag_w + 10
    for i, line in enumerate(lines):
        if i > 0:
            lx = x
        draw_text(cv, lx, y, line, 2, 3, INK, spacing=0)
        y += 23
    return y


def build():
    cv = Canvas(W, H, PAPER)

    # masthead
    draw_text_centered(cv, 8, "THE WORLD IN ONE DAY", 2, 2, RED,
                       bold=False, spacing=8)
    draw_text_centered(cv, 26, "WEDNESDAY 18 NOVEMBER 2026", 7, 8, INK,
                       bold=True, spacing=1)
    cv.hline(MX, 88, CW, INK, 3)
    cv.hline(MX, 94, CW, INK, 1)

    # lead story (left)
    lx, lw = MX, 606
    draw_text(cv, lx, 100, "KERCH BRIDGE", 8, 8, INK, bold=True, spacing=2)
    draw_text(cv, lx, 158, "DESTROYED", 8, 8, INK, bold=True, spacing=2)
    draw_bridge(cv, lx, 216, lw, 48)
    lead_body = ("Road arch of the 19-km Crimea bridge crumbled into the "
                 "sea after two nights of strikes. Reuters-verified video. "
                 "Two killed; road closed, rail partly resumed. Part of "
                 "Ukraine's biggest drone wave yet: 1,441 drones over "
                 "22 regions.")
    draw_wrapped(cv, lx, 270, lead_body, lw, 2, 3, INK, spacing=0,
                 line_gap=3)

    # second lead (right)
    sx0, sw = 656, 350
    cv.vline(640, 100, 296, LIGHT, 2)
    draw_text(cv, sx0, 100, "HORMUZ: STRAIT", 4, 5, INK, bold=True, spacing=2)
    draw_text(cv, sx0, 136, "NEARLY SHUT", 4, 5, RED, bold=True, spacing=2)
    draw_tanker(cv, sx0, 182, sw, 52)  # tanker illustration
    hormuz_body = ("US jets struck an IRGC missile site on Qeshm Island "
                   "after drones targeted a US radar site in Bahrain. "
                   "Ships ablaze near the strait; LPG carrier Tara Gas "
                   "disabled. Third US carrier arrives; crossings "
                   "nearly stop.")
    draw_wrapped(cv, sx0, 234, hormuz_body, sw, 2, 3, INK, spacing=0,
                 line_gap=3)

    cv.hline(MX, 408, CW, INK, 2)  # rule under the leads

    # panel rows
    pw = 321
    xs = (MX, MX + pw + 12, MX + 2 * (pw + 12))
    row1 = (
        ("building", "APEC OPENS IN SHENZHEN",
         "Xi urges open trade. Putin's first in-person APEC since 2017. "
         "Trump lands tonight; first Trump-Xi-Putin summit set for "
         "Thursday."),
        ("quad", "QUAD MEETS IN MANILA",
         "Trump, Modi, Takaichi and Albanese hold the first Quad summit "
         "in two years: joint sea patrols and an AI plan announced."),
        ("sun", "COP31 DEADLOCK",
         "Ministers take over in Antalya as the draft splits on fossil "
         "fuels and $120bn-a-year adaptation aid. The Friday close "
         "may slip."),
    )
    row2 = (
        ("tent", "GAZA WINTER EMERGENCY",
         "IOM warns more hypothermia deaths are 'inevitable' without "
         "shelter. 1.7 million displaced; 100,000 tents wait to enter."),
        ("storm", "CYCLONE AKVAN NEARS INDIA",
         "A severe cyclone at 100-110 km/h aims at the Andhra coast: "
         "landfall Friday near Nellore. Orange alert stands."),
        ("cross", "EBOLA IN DR CONGO",
         "Cases pass 11,300 and deaths near 5,500 in the Bundibugyo "
         "outbreak. No approved vaccine; children under five hit "
         "hardest."),
    )
    for row, ry in ((row1, 418), (row2, 586)):  # the two panel rows
        for i, (icon, head, body) in enumerate(row):
            if i:
                cv.vline(xs[i] - 7, ry, 150, LIGHT, 2)
            panel(cv, xs[i], ry, pw, icon, head, body)
    cv.hline(MX, 580, CW, LIGHT, 2)
    cv.hline(MX, 750, CW, INK, 2)

    # briefs
    draw_text(cv, MX, 756, "AROUND THE WORLD IN BRIEF", 3, 3, RED,
              bold=True, spacing=2)
    briefs_left = (
        ("ASIA:", "North Korea fires a ballistic missile into the Sea "
                  "of Japan"),
        ("AFRICA:", "Drone strike on a Nyala market in Sudan kills "
                    "at least 21"),
        ("AMERICAS:", "Peltola win gives US Democrats a 56-44 Senate "
                      "majority"),
        ("SOUTH AMERICA:", "Ecuador fishermen sue the US over a drone "
                           "strike"),
    )
    briefs_right = (
        ("ASIA:", "Japan scrambles jets over a suspected Russian "
                  "airspace entry"),
        ("OCEANIA:", "Cyclone Xavier reaches Category 5 near the "
                     "Cook Islands"),
        ("EUROPE:", "Estonia to close its Russia border crossings "
                    "from December"),
        ("CULTURE:", "GTA VI launches at midnight after years of "
                     "waiting"),
    )
    by = 784
    for tag, rest in briefs_left:
        by = draw_brief(cv, MX, by, 470, tag, rest) + 3
    by = 784
    for tag, rest in briefs_right:
        by = draw_brief(cv, 526, by, 480, tag, rest) + 3
    cv.vline(508, 784, 180, LIGHT, 2)  # briefs column divider

    # footer
    cv.hline(MX, 980, CW, INK, 2)
    footer_main = "18 November 2026 \u00b7 16 stories \u00b7 6 continents \u00b7 one page"
    draw_text_centered(cv, 986, footer_main, 2, 2, INK, bold=True, spacing=2)
    footer_src = "Compiled from the day's Reuters, UN, UKMTO and IMD reports."
    draw_text_centered(cv, 1002, footer_src, 2, 2, GREY, bold=False, spacing=2)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    size = write_png(cv, os.path.join(out_dir, "entry.png"))
    print("wrote entry.png", size, "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
