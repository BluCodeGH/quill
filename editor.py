import curses
import colors

def nc(coords):
  return coords[1], coords[0]

class Editor:
  def __init__(self, term):
    self.term = term
    colors.go()
    text = Text("hello world\nthis is a test\nffffffgfffffgfffffffffgffffffgffff", colors.color(colors.WHITE, colors.GRAY))
    t = TextBox(text, (0, 0), (15, 20), True)
    while True:
      k = t.term.getkey()
      if k == "q":
        break
      elif k == "=":
        self.term.redrawwin()
        self.term.refresh()
        t.resize(t.pos, (t.size[0] + 1, t.size[1] + 1))
      elif k == "-":
        self.term.redrawwin()
        self.term.refresh()
        t.resize(t.pos, (t.size[0] - 1, t.size[1] - 1))
      elif k == "r":
        self.term.redrawwin()
        self.term.refresh()
        t.resize((t.pos[0] + 1, t.pos[1]), t.size)
      elif k == "l":
        self.term.redrawwin()
        self.term.refresh()
        t.resize((t.pos[0] - 1, t.pos[1]), t.size)
      else:
        t.handle(k)

class TextBox:
  def __init__(self, text, pos, size, wrap=True):
    self.text = text
    self.pos = pos
    self.size = size
    self.offset = [0, 0]
    self.cursor = [0, 0]
    self.cursori = 0
    self.wrap = wrap
    self.term = curses.newpad(1, 1)
    self.term.keypad(1)

    self.reflow()

  def resize(self, pos, size):
    self.pos = pos
    self.size = size
    self.reflow()

  def reflow(self):
    if self.wrap:
      self.text.reflow(self.size[0])
    else:
      self.text.reflow()
    self.getpad()
    for i in range(len(self.text)):
      res = self.text.getch(i)
      if res[2] is not None:
        try:
          self.term.addstr(*res)
        except:
          raise Exception(res)
    self.update()

  def update(self):
    pos2 = self.pos[1] + self.size[1] - 1, self.pos[0] + self.size[0] - 1
    y, x, *_ = self.text.getch(self.cursori)
    self.moveOffset(x, y)
    self.term.move(y, x)
    self.term.refresh(*nc(self.offset), *nc(self.pos), *pos2)

  def getpad(self):
    dx = max(self.size[0], self.text.size[0])
    dy = max(self.size[1], self.text.size[1])
    self.term.resize(dy, dx)
    for x in range(dx):
      for y in range(dy):
        try:
          self.term.addstr(y, x, " ", self.text.defaultTheme)
        except curses.error:
          pass

  def handle(self, inp):
    if inp == "KEY_RIGHT":
      self.movex(1)
    elif inp == "KEY_LEFT":
      self.movex(-1)
    elif inp == "KEY_UP":
      self.movey(-1)
    elif inp == "KEY_DOWN":
      self.movey(1)
    else:
      self.text.contents += "\n" + inp
      self.reflow()

  def movex(self, d):
    self.cursori += d
    self.cursori = max(min(self.cursori, len(self.text)), 0)
    y, x, *_ = self.text.getch(self.cursori)
    self.cursor = (x, y)
    self.update()

  def movey(self, d):
    self.cursor = self.cursor[0], max(min(self.cursor[1] + d, self.text.size[1] - 1), 0)
    self.cursori = self.text.getpos(*self.cursor)
    self.update()

  def moveOffset(self, x, y):
    if y < self.offset[1] + 1:
      self.offset[1] -= self.offset[1] + 1 - y
    if y > self.offset[1] + self.size[1] - 2:
      self.offset[1] += y - (self.offset[1] + self.size[1] - 2)
    if x < self.offset[0] + 1:
      self.offset[0] -= self.offset[0] + 1 - x
    if x > self.offset[0] + self.size[0] - 1:
      self.offset[0] += x - (self.offset[0] + self.size[0] - 1)

class Text:
  nonPrinting = "\r\n"
  def __init__(self, contents, col):
    self.contents = contents
    self.themes = [(10, 20, colors.color(colors.RED, colors.BLUE))]
    self.defaultTheme = col
    self.lines = [0]
    self.size = None

  def reflow(self, wrap=False):
    dx = wrap or 0
    self.lines = [0]
    for i, c in enumerate(self.contents + " "):
      if c == "\n":
        self.lines.append(i + 1)
      elif wrap and i - self.lines[-1] == wrap:
        self.lines.append(i)
      elif not wrap and i - self.lines[-1] + 1 > dx:
        dx = i - self.lines[-1] + 1
    self.lines.append(len(self.contents) + 1)
    self.size = (dx + 1, len(self.lines) - 1)

  def getch(self, i):
    char = (self.contents + " ")[i]
    if char in self.nonPrinting:
      char = None
    y = -1
    for l in self.lines:
      if l > i:
        break
      y += 1
    x = i - self.lines[y]
    theme = self.defaultTheme
    for t in self.themes:
      if t[0] <= i and t[1] > i:
        theme = t[2]
    return y, x, char, theme

  def getpos(self, x, y):
    i = self.lines[y]
    if self.lines[y + 1] - self.lines[y] - 1 < x:
      return self.lines[y + 1] - 1
    return i + x

  def __len__(self):
    return len(self.contents)
