import logging
import term
logging.basicConfig(filename='quill.log', level=logging.DEBUG, format="%(message)s")
logging.info("Starting quill.")

class Text:
  jump = [5, 1] # distance to jump when the cursor goes off screen
  def __init__(self, pos, size, wrap=True):
    self.pos = pos # position of the upper left corner of the view
    self.size = size # size of the view
    self.cursor = [0, 0] # coords of the cursor relative to the upper left corner of the document
    self.scroll = [0, 0] # coords of the upper left corner of the view relative to the document
    self.wrap = wrap
    self.buffer = ""
    self.cursori = 0 # reflected position of the cursor
    self.linesi = []
    self.redisplay()

  def redisplay(self):
    start = self.scroll[1]
    end = self.scroll[1] + self.size[1]
    for i, (s, e) in enumerate(zip(([0] + self.linesi)[start:end], (self.linesi + [len(self.buffer)])[start:end])):
      term.move(self.pos[0], self.pos[1] + i)
      for c in self.buffer[s:e][self.scroll[0]:self.size[0]]:
        if c != "\n":
          term.write(c)
      term.write(" " * (self.size[0] - e + s))
    complete = len((self.linesi + [len(self.buffer)])[start:end])
    for i in range(self.size[1] - complete):
      term.move(self.pos[0], self.pos[1] + i + complete)
      term.write(" " * self.size[0])

  def getCursor(self):
    s = ([0] + self.linesi)[self.cursor[1]]
    e = (self.linesi + [len(self.buffer)])[self.cursor[1]]
    logging.debug(str((s, e, self.cursor[1])))
    res = [min(self.cursor[0], e - s), self.cursor[1]]
    self.cursori = s
    self.cursori += res[0]
    logging.debug(str(res))
    return res

  def setCursor(self):
    for i, l in enumerate(self.linesi + [len(self.buffer) + 1]):
      if self.cursori < l:
        self.cursor[1] = i
        self.cursor[0] = self.cursori - ([0] + self.linesi)[i]
        logging.debug("s" + str(self.cursor))
        break

  def doScroll(self):
    c = self.getCursor()
    if c[0] - self.scroll[0] == self.size[0] and not self.wrap:
      self.scroll[0] += 1
    if c[0] - self.scroll[0] < 0 and not self.wrap:
      self.scroll[0] -= 1
    if c[1] - self.scroll[1] == self.size[1]:
      self.scroll[1] += 1
    if c[1] - self.scroll[1] < 0:
      self.scroll[1] -= 1

  def update(self):
    c = self.getCursor()
    #self.doScroll()
    self.redisplay()
    term.move(self.pos[0] + c[0] - self.scroll[0], self.pos[1] + c[1] - self.scroll[1])

  def write(self, text):
    self.buffer = self.buffer[:self.cursori] + text + self.buffer[self.cursori:]
    x = 0
    self.linesi = []
    for i, c in enumerate(self.buffer):
      x += 1
      if x > self.size[0]:
        self.linesi.append(i)
        x = 0
      if c == "\n":
        self.linesi.append(i + 1)
        x = 0
    self.cursori += len(text)
    logging.debug(str([self.buffer, self.linesi, self.cursori]))
    self.setCursor()
    self.update()

  def handle(self, key):
    if key == "right":
      self.cursor[0] = min(self.size[0], self.cursor[0] + 1)
      self.update()
    elif key == "left":
      self.cursor[0] = max(0, self.cursor[0] - 1)
      self.update()
    elif key == "down":
      self.cursor[1] = min(self.size[1], self.cursor[1] + 1)
      self.update()
    elif key == "up":
      self.cursor[1] = max(0, self.cursor[1] - 1)
      self.update()
    else:
      self.write(key)

def main():
  term.color(0, 7)
  term.clear()
  term.color(7, 0)
  T = Text((0, 0), (10, 10), wrap=True)
  # T.buffer = "abcdefghijklmnopqrstuvwxyz"
  # T.linesi = [3, 7, 20, 25]
  # T.scroll = [1, 1]
  # T.redisplay()
  # term.getkey()
  # T.updateCursor()
  k = term.getkey()
  while k != "^C":
    T.handle(k)
    k = term.getkey()

term.wrapper(main)
