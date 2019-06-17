import term

class Text:
  jump = [5, 1] # distance to jump when the cursor goes off screen
  def __init__(self, pos, size, wrap=True):
    self.pos = pos # position of the upper left corner of the view
    self.size = size # size of the view
    self.cursor = [0, 0] # coords of the cursor relative to the upper left corner of the view
    self.scroll = [0, 0] # coords of the upper left corner of the view relative to the document
    self.wrap = wrap
    self.buffer = ""
    self.cursori = 0
    self.redisplay()

  def resolve(self):
    return self.pos[0] + self.cursor[0], self.pos[1] + self.cursor[1]

  def redisplay(self):
    splitlines = self.buffer.split("\n")
    lines = []
    for i, line in enumerate(splitlines):
      if self.wrap:
        lines += [line[i:i+self.size[0]] for i in range(0, len(line), self.size[0])]
      else:
        lines.append(line)
    lines += ["" for _ in range(self.size[1] + self.scroll[1] - len(lines))]
    lines = lines[self.scroll[1]:self.scroll[1] + self.size[1]]
    for i, line in enumerate(lines):
      term.move(self.pos[0], self.pos[1] + i)
      for j, c in enumerate(line[self.scroll[0]:self.scroll[0] + self.size[0]] + "\n"):
        if c == "\n":
          term.write(" " * (self.size[0] - j))
        else:
          term.write(c)

  def updateCursor(self):
    splitlines = self.buffer.split("\n")
    lines = []
    for i, line in enumerate(splitlines):
      if i + 1 < len(splitlines):
        line += "\n"
      if self.wrap:
        lines += [line[i:i+self.size[0]] for i in range(0, len(line), self.size[0])]
      else:
        lines.append(line)
    i = 0
    self.cursor = [0, 0]
    for line in lines:
      if i + len(line) >= self.cursori:
        idx = self.cursori - i
        if idx == self.size[0]:
          self.cursor[1] += 1
        elif idx > 0 and line[idx - 1] == "\n":
          self.cursor[1] += 1
        else:
          self.cursor[0] = idx
        break
      i += len(line)
      self.cursor[1] += 1

  def doScroll(self):
    if self.cursor[0] - self.scroll[0] == self.size[0] and not self.wrap:
      self.scroll[0] += self.jump[0]
    if self.cursor[0] - self.scroll[0] < 0 and not self.wrap:
      self.scroll[0] -= self.jump[0]
    if self.cursor[1] - self.scroll[1] == self.size[1]:
      self.scroll[1] += self.jump[1]
    if self.cursor[1] - self.scroll[1] < 0:
      self.scroll[1] -= self.jump[1]

  def update(self):
    self.updateCursor()
    self.doScroll()
    self.redisplay()
    term.move(self.pos[0] + self.cursor[0] - self.scroll[0], self.pos[1] + self.cursor[1] - self.scroll[1])

  def write(self, text):
    self.update()
    self.buffer = self.buffer[:self.cursori] + text + self.buffer[self.cursori:]
    for c in text:
      self.cursori += 1
      if c != "\n":
        term.write(c)
      self.update()

  def handle(self, key):
    if key == "right":
      if self.cursori < len(self.buffer):
        self.cursori += 1
        self.update()
    elif key == "left":
      if self.cursori > 0:
        self.cursori -= 1
        self.update()
    else:
      self.write(key)

def main():
  term.color(0, 7)
  term.clear()
  term.color(7, 0)
  T = Text((0, 0), (10, 10))
  T.updateCursor()
  k = term.getkey()
  while k != "^C":
    T.handle(k)
    k = term.getkey()

term.wrapper(main)
