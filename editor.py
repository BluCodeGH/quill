import os.path

import colors
from text import TextBox
from shortcuts import Shortcuts

class Editor:
  def __init__(self, term, pos, size, quill):
    self.term = term
    self.size = size
    self.main = TextBox(colors.color(colors.WHITE, colors.BG), pos, (size[0], size[1] - 1))
    self.bar = TextBox(colors.color(colors.WHITE, colors.GRAY), (pos[0], pos[1] + size[1] - 1), (size[0], 1), False)
    self.keybuf = []
    self.ongoing = False
    self.shortcuts = Shortcuts("shortcuts.map", quill, self)
    self.meta = {"name": "untitled"}
    self.statusbar()

  def work(self):
    k = self.main.getkey()
    sk = self.shortcuts.go([k])
    if sk is None:
      self.main.handle(k)
      self.statusbar()
    elif sk:
      keybuf = [k]
      while sk:
        self.status(" ".join(keybuf) + " ", True)
        cil = self.bar.cursori
        while True:
          k = self.bar.getkey()
          if self.bar.cursori == cil and k in ["KEY_BACKSPACE", "KEY_LEFT"]:
            continue
          if k == "KEY_ESC":
            self.statusbar()
            return
          if k == "\n":
            keybuf.append(self.bar.text.contents[cil:])
            break
          if len(k) > 1 and k[0] in "^_":
            if len(self.bar.text.contents[cil:]) > 0:
              keybuf.append(self.bar.text.contents[cil:])
            keybuf.append(k)
            break
          self.bar.handle(k)
        sk = self.shortcuts.go(keybuf)
        if sk is None:
          self.status("Invalid shortcut: " + " ".join(keybuf))

  def status(self, message, stay=False):
    self.bar.set(message)
    if not stay:
      self.main.update()

  fileTypes = {".txt":"Text", ".py":"Python", "":"Text"}
  def statusbar(self):
    lc = " L{},C{}".format(self.main.cursor[1] + 1, self.main.cursor[0])
    ftype = os.path.splitext(self.meta["name"])[1]
    ftype = self.fileTypes.get(ftype, ftype)
    padding = " " * (self.size[0] - len(lc) - len(ftype) - 1)
    self.status(lc + padding + ftype)

  def prompt(self, message, default=""):
    self.status(message + default, True)
    cil = len(message)
    while True:
      ci = self.bar.cursori
      k = self.bar.getkey()
      if ci == cil and k in ["KEY_BACKSPACE", "KEY_LEFT"]:
        continue
      if k == "KEY_ESC":
        return None
      if k == "\n":
        return self.bar.text.contents[cil:]
      self.bar.handle(k)

  def resize(self, pos, size):
    self.main.resize(pos, (size[0], size[1] - 1))
    self.bar.resize((pos[0], pos[1] + size[1] - 1), (size[0], 1))
