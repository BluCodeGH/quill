import curses

def nc(coords):
  return coords[1], coords[0]

class TextBox:
  def __init__(self, theme, pos, size, wrap=True):
    self.text = Text("")
    self.theme = theme
    self.pos = pos
    self.size = size
    self.offset = [0, 0]
    self.cursor = [0, 0]
    self.cursori = 0
    self.wrap = wrap
    self.term = curses.newpad(1, 1)
    self.term.keypad(1)
    self.selection = [0, 0]

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
        if i >= self.selection[0] and i < self.selection[1]:
          self.term.addstr(*res, self.theme | curses.A_REVERSE)
        else:
          self.term.addstr(*res, self.theme)
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
          self.term.addstr(y, x, " ", self.theme)
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
    elif inp == "KEY_BACKSPACE":
      if self.cursori > 0:
        self.text.delete(self.cursori - 1, 1)
        self.movex(-1)
        self.reflow()
    else:
      self.text.insert(self.cursori, inp)
      self.reflow()
      self.movex(len(inp))

  def write(self, text):
    self.text.insert(self.cursori, text)
    self.reflow()
    self.movex(len(text))

  def set(self, text):
    self.text.set(text)
    self.cursori = len(text)
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
    if self.size[1] >= 3:
      if y < self.offset[1] + 1:
        self.offset[1] -= self.offset[1] + 1 - y
      if y > self.offset[1] + self.size[1] - 2:
        self.offset[1] += y - (self.offset[1] + self.size[1] - 2)
    else:
      if y < self.offset[1]:
        self.offset[1] -= self.offset[1] - y
      if y > self.offset[1] + self.size[1] - 1:
        self.offset[1] += y - (self.offset[1] + self.size[1] - 1)
    if x < self.offset[0] + 1:
      self.offset[0] -= self.offset[0] + 1 - x
    if x > self.offset[0] + self.size[0] - 1:
      self.offset[0] += x - (self.offset[0] + self.size[0] - 1)

  keysubs = {8: "KEY_BACKSPACE", 9: "\t", 10: "\n"}
  def getkey(self, blocking=True):
    if not blocking:
      curses.halfdelay(1)
      try:
        k = self.term.getkey()
      except curses.error:
        return None
      finally:
        curses.raw()
    else:
      k = self.term.getkey()
    if len(k) > 1:
      return k
    if ord(k) <= 26 and ord(k) not in self.keysubs:
      k = "^" + chr(ord(k) + 64)
    elif ord(k) == 27:
      k2 = self.getkey(False)
      if k2:
        return "_" + k2
      return "KEY_ESC"
    else:
      k = self.keysubs.get(ord(k), k)
    return k

class Text:
  nonPrinting = "\r\n"
  def __init__(self, contents):
    self.contents = contents
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
    return y, x, char

  def getpos(self, x, y):
    i = self.lines[y]
    if self.lines[y + 1] - self.lines[y] - 1 < x:
      return self.lines[y + 1] - 1
    return i + x

  def set(self, s):
    self.contents = s

  def insert(self, i, s):
    self.contents = self.contents[:i] + s + self.contents[i:]

  def delete(self, i, n):
    self.contents = self.contents[:i] + self.contents[i + n:]

  def __len__(self):
    return len(self.contents)
