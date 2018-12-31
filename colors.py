import curses

def mkcol(i, h):
  r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
  curses.init_color(i, int(r * 3.9), int(g * 3.9), int(b * 3.9))

BG=0
WHITE=1
GRAY=2
RED=3
GREEN=4
YELLOW=5
BLUE=6
MAGENTA=7
CYAN=8

STD=1
GD=2
GL=3
GB=4

def go():
  mkcol(BG, "242424")
  mkcol(WHITE, "e0e0e0")
  mkcol(GRAY, "6a6a6a")
  mkcol(RED, "fb0120")
  mkcol(GREEN, "a1c659")
  mkcol(YELLOW, "fda331")
  mkcol(BLUE, "6fb3d2")
  mkcol(MAGENTA, "d381c3")
  mkcol(CYAN, "76c7b7")

_pairs = {"I":1}

def color(fg, bg):
  if (fg, bg) not in _pairs:
    curses.init_pair(_pairs["I"], fg, bg)
    _pairs[(fg, bg)] = _pairs["I"]
    _pairs["I"] += 1
  return curses.color_pair(_pairs[(fg, bg)])
