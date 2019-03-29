import os
import select
import sys
import termios

esc = "\x1B"
csi = esc + "["

try:
  size = os.get_terminal_size(1)
except OSError:
  print("Error, quill does not support non-terminal interfaces.")
  sys.exit(1)

def _out(s):
  sys.stdout.write(csi + s)
  sys.stdout.flush()

def wrapper(fn, alternate=True):
  fd = sys.stdin.fileno()
  original = termios.tcgetattr(fd)
  new = termios.tcgetattr(fd)
  try:
    # ignore break, ignore cr, disable on/off via ctrl+s/q
    new[0] &= ~(termios.BRKINT | termios.IGNCR | termios.IXON)
    # disable 'implimentation-specific output handling', map outputed NL to CRNL
    new[1] &= ~(termios.OPOST)
    # set output character size to 8 bits
    new[2] &= ~termios.CSIZE
    new[2] |= termios.CS8
    # disable echo, disable canonical mode (line buffering and basic editing), disable 'implementation defined input processing', disable signals
    new[3] &= ~(termios.ECHO | termios.ICANON | termios.IEXTEN | termios.ISIG)
    # return data after every 1 character, wait 0.0 seconds before doing so.
    new[6][termios.VMIN] = 0
    new[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSADRAIN, new)
    if alternate:
      _out("?1049h")
    fn()
  finally:
    termios.tcsetattr(fd, termios.TCSADRAIN, original)
    if alternate:
      _out("?1049l")

"""
keymaps:
normal keys = their ascii values
bs = 127
del = 27 91 51 126
ctrl a-z = 1 - 26
ctrl:
  ` = 0
  ' ' = 0
  ? = 31
  | = 27
  2 = 0
  3-8 = 27-31
alt: 27 __
esc: 27
f1-4: 27 79 80-83
f5-8: 27 91 49 [53,55,56,57] 126
f9-12: 27 91 50 [48,49,51,51] 126
ctrl+f1-4: 27 91 49 59 53 80-83
ctrl+f5-8: 27 91 49 [53,55,56,57] 59 53 126
ctrl+f9-12: 27 91 50 [48,49,51,52] 59 53 126
udrl: 27 91 [65,66,67,68]
ctrl udrl: 27 91 49 59 53 [65,66,67,68]
pu/pd: 27 91 [53,54] 126
ctrl pu/pd: 27 91 [53,54] 59 53 126
h/e: 27 91 [72,70]
ctrl h/e: 27 91 49 59 53 [72,70]
alt+special: same as above replacing 59 53 with 59 51
shift+special: same as above replace 59 53 with 59 50
"""

modMap = {
    27:{
        None:"esc",
        -1:"_",
        79:{
            80:"f1",
            81:"f2",
            82:"f3",
            83:"f4"
        }, 91:{
            49:{
                53:{
                    126:"f5",
                    59:{
                        53:{126:"^f5"},
                        51:{126:"_f5"},
                        50:{126:"F5"}
                    }
                }, 55:{
                    126:"f6",
                    59:{
                        53:{126:"^f6"},
                        51:{126:"_f6"},
                        50:{126:"F6"}
                    }
                }, 56:{
                    126:"f7",
                    59:{
                        53:{126:"^f7"},
                        51:{126:"_f7"},
                        50:{126:"F7"}
                    }
                }, 57:{
                    126:"f8",
                    59:{
                        53:{126:"^f8"},
                        51:{126:"_f8"},
                        50:{126:"F8"}
                    }
                }, 59: {
                    53: {
                        80:"^f1",
                        81:"^f2",
                        82:"^f3",
                        83:"^f4",
                        65: "^up",
                        66: "^down",
                        67: "^right",
                        68: "^left"
                    },
                    51: {
                        80:"_f1",
                        81:"_f2",
                        82:"_f3",
                        83:"_f4",
                        65: "_up",
                        66: "_down",
                        67: "_right",
                        68: "_left"
                    },
                    50: {
                        80:"F1",
                        81:"F2",
                        82:"F3",
                        83:"F4",
                        65: "UP",
                        66: "DOWN",
                        67: "RIGHT",
                        68: "LEFT"
                    }
                }
            }, 50:{
                48:{
                    126:"f9",
                    59:{
                        53:{126:"^f9"},
                        51:{126:"_f9"},
                        50:{126:"F9"}
                    }
                }, 49:{
                    126:"f10",
                    59:{
                        53:{126:"^f10"},
                        51:{126:"_f10"},
                        50:{126:"F10"}
                    }
                }, 51:{
                    126:"f11",
                    59:{
                        53:{126:"^f11"},
                        51:{126:"_f11"},
                        50:{126:"F11"}
                    }
                }, 52:{
                    126:"f12",
                    59:{
                        53:{126:"^f12"},
                        51:{126:"_f12"},
                        50:{126:"F12"}
                    }
                }
            }, 65: "up",
            66: "down",
            67: "right",
            68: "left",
            53: {126:"pageUp"},
            54: {126:"pageDown"},
            72: "home",
            70: "end",
            51: {126:"del"}
        }
    },
    127:"bs"
}
symMap = {
    "^J":"\n",
    "^I":"\t"
}

def getkey():
  keyBuf = []
  select.select([sys.stdin], [], [])
  while True:
    c = sys.stdin.read(1)
    if c == "":
      res = _process(keyBuf, modMap)
      if res in symMap:
        return symMap[res]
      return res
    keyBuf.append(ord(c))


def _process(keyBuf, mmap):
  if not keyBuf:
    key = None
  key = keyBuf[0]
  if key in mmap:
    if isinstance(mmap[key], dict):
      return _process(keyBuf[1:], mmap[key])
    return mmap[key]
  if -1 in mmap:
    return mmap[-1] + _process(keyBuf, modMap)
  if key < 27:
    return "^" + chr(key + 64)
  if key < 32:
    return "^" + chr(key + 24)
  return chr(key)

def write(s):
  sys.stdout.write(s.replace("\n", "\r\n"))
  sys.stdout.flush()

def move(x, y):
  _out("{};{}H".format(x, y))

def clear():
  _out("2J")

def save():
  _out("s")
def restore():
  _out("u")

def reset():
  _out("0m")
def bold():
  _out("1m")
def dim():
  _out("2m")
def underline():
  _out("4m")
def reverse():
  _out("7m")
def strikethrough():
  _out("9m")
def doubleUnderline():
  _out("21m")

def color(fg, bg):
  if fg > 7:
    fg += 53
  if bg > 7:
    bg += 53
  fg += 30
  bg += 40
  _out(str(fg) + "m")
  _out(str(bg) + "m")

def rgbColor(fg, bg):
  _out("38;2;{};{};{}m".format(*fg))
  _out("48;2;{};{};{}m".format(*bg))

def resetColor():
  _out("39;49m")
