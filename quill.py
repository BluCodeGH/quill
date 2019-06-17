import curses
import os

from editor import Editor
import colors
from shortcuts import Shortcuts

class Quill:
  def __init__(self, term):
    self.term = term
    colors.go()
    self.size = term.getmaxyx()
    self.size = self.size[1], self.size[0]
    self.editors = [Editor(self.term, (0, 0), self.size, self)]
    self.bar = None
    self.focus = 0
    self.running = True

  def go(self):
    while self.running:
      self.editors[self.focus].work()

  def newtab(self):
    if not self.bar:
      self.bar = curses.newpad(1, (self.size[1]))
      self.editors[0].term.resize(self.size[1] - 1, self.size[0])
      self.editors[0].resize((0, 1), (self.size[0], self.size[1] - 1))
    self.focus += 1
    self.editors.insert(self.focus, Editor(self.term, (0, 1), (self.size[0], self.size[1] - 1), self))
    self.drawbar()

  def closetab(self, i=None):
    i = i or self.focus
    self.editors.pop(i)
    self.focus = max(self.focus - 1, 0)
    if len(self.editors) == 1:
      self.editors[0].term.resize(self.size[1], self.size[0])
      self.editors[0].resize((0, 0), self.size)
    elif len(self.editors) == 0:
      self.running = False
      return
    self.editors[self.focus].main.update()
    self.editors[self.focus].bar.update()
    self.drawbar()

  def switchtab(self, i):
    self.focus = i
    self.editors[self.focus].main.update()
    self.editors[self.focus].bar.update()
    self.drawbar()

  def drawbar(self):
    if not self.bar:
      return
    names = [e.meta["name"] for e in self.editors]
    size = max(self.size[0], len(" | ".join(names))) + 1
    self.bar.resize(1, size)
    self.bar.addstr(0, 0, " " * (self.bar.getmaxyx()[1] - 1), colors.color(colors.WHITE, colors.GRAY))
    self.bar.move(0, 0)
    for i, name in enumerate(names):
      fmt = colors.color(colors.WHITE, colors.GRAY)
      if i != 0:
        self.bar.addstr(" | ", fmt)
      if i == self.focus:
        fmt = self.editors[self.focus].main.theme
      self.bar.addstr(name, fmt)
    self.bar.refresh(0, 0, 0, 0, 1, self.size[0] - 1)
    self.editors[self.focus].main.update()

def main(term):
  curses.raw()
  q = Quill(term)
  q.go()

os.environ.setdefault('ESCDELAY', '10')
curses.wrapper(main)
