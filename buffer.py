import logging
import term

class Buffer:
  border = [5, 1] # distance from edge of view to start scrolling at
  def __init__(self, pos, size, wrap=True):
    self.pos = pos # position of the upper left corner of the view
    self.size = size # size of the view
    self.cursor = [0, 0] # coords of the cursor relative to the upper left corner of the document
    self.scroll = [0, 0] # coords of the upper left corner of the view relative to the document
    self.wrap = wrap
    self.buffer = ""
    self.cursori = 0 # reflected position of the cursor within buffer
    self.linesi = [] # indexes of the first character in each line, excluding 0
    logging.info("Started buffer at %d, %d", *pos)

  # draw the current contents to the screen
  def draw(self):
    startLine = self.scroll[1]
    endLine = min(self.scroll[1] + self.size[1], len(self.linesi) + 1) # cap endLine to the end of the buffer
    for i in range(startLine, endLine):
      starti = ([0] + self.linesi)[i] # start and end index of this line
      endi = (self.linesi + [len(self.buffer)])[i]
      term.move(self.pos[0], self.pos[1] - startLine + i)
      starti += self.scroll[0]
      endi = max(min(endi, starti + self.size[0]), starti) # ensure starti <= endi and endi fits on screen
      for c in self.buffer[starti:endi]:
        if c != "\n":
          term.write(c)
        else:
          term.write(" ")
      term.write(" " * (self.size[0] - endi + starti)) # erase till end of line
    complete = endLine - startLine
    for i in range(self.size[1] - complete):
      term.move(self.pos[0], self.pos[1] + i + complete)
      term.write(" " * self.size[0])
    c = self.getPos(self.cursori)
    term.move(self.pos[0] + c[0] - self.scroll[0], self.pos[1] + c[1] - self.scroll[1])

  # get the nearest buffer index given a position
  def getCursori(self, coords):
    s = ([0] + self.linesi)[coords[1]]
    e = (self.linesi + [len(self.buffer) + 1])[coords[1]]
    cursori = s
    cursori += min(coords[0], e - s - 1)
    return cursori

  # get the position of a character in the buffer
  def getPos(self, index):
    res = [None, None]
    for i, l in enumerate(self.linesi + [len(self.buffer) + 1]):
      if index < l:
        res[1] = i
        res[0] = index - ([0] + self.linesi)[i]
        break
    return res

  # update self.scroll to reflect the current cursor index
  def doScroll(self):
    c = self.getPos(self.cursori)
    if c[0] - self.scroll[0] >= self.size[0] - self.border[0] + 1 and not self.wrap:
      self.scroll[0] = c[0] - self.size[0] + self.border[0]
    if c[0] - self.scroll[0] <= self.border[0] and not self.wrap:
      self.scroll[0] = max(c[0] - self.border[0], 0)
    if c[1] - self.scroll[1] >= self.size[1] - self.border[1]:
      self.scroll[1] = c[1] - self.size[1] + self.border[1] + 1
    if c[1] - self.scroll[1] <= self.border[1]:
      self.scroll[1] = max(c[1] - self.border[1], 0)

  # write characters to the buffer
  def write(self, text):
    self.buffer = self.buffer[:self.cursori] + text + self.buffer[self.cursori:]
    start = len(self.linesi) # line index to start from
    for i, l in enumerate(self.linesi):
      if l > self.cursori:
        start = i
        break
    x = self.cursori - ([0] + self.linesi)[start] # current offset of cursor
    newLinesi = []
    end = len(self.linesi) # (old) line index where things match up again
    for i, c in enumerate(self.buffer[self.cursori:]):
      x += 1
      if x > self.size[0] and self.wrap:
        x = 1
        # if this newline causes it to match up with the old linesi
        if i >= len(text) and self.cursori + i - len(text) in self.linesi:
          end = self.linesi.index(self.cursori + i - len(text))
          break
        newLinesi.append(self.cursori + i)
      if c == "\n":
        x = 0
        # if this newline causes it to match up with the old linesi
        if i >= len(text) and self.cursori + i + 1 - len(text) in self.linesi:
          end = self.linesi.index(self.cursori + i + 1 - len(text))
          break
        newLinesi.append(self.cursori + i + 1)
    self.linesi[start:end] = newLinesi
    for i in range(start + len(newLinesi), len(self.linesi)):
      self.linesi[i] += len(text) # updated old matched up linesi
    self.cursori += len(text)
    self.cursor = self.getPos(self.cursori)
    self.doScroll()

  # replace the contents of the buffer
  def set(self, text):
    self.buffer = text
    x = 0
    self.linesi = []
    for i, c in enumerate(self.buffer):
      x += 1
      if x > self.size[0] and self.wrap:
        self.linesi.append(i)
        x = 1
      if c == "\n":
        self.linesi.append(i + 1)
        x = 0
    self.cursori = 0
    self.cursor = self.getPos(self.cursori)
    self.doScroll()

  # delete n characters starting at index starti
  def delete(self, starti, n):
    self.cursori = starti
    self.buffer = self.buffer[:starti] + self.buffer[starti+n:]
    start = len(self.linesi) # line index to start from
    for i, l in enumerate(self.linesi):
      if l > self.cursori:
        start = i
        break
    x = self.cursori - ([0] + self.linesi)[start] # current offset of cursor
    newLinesi = []
    end = len(self.linesi) # (old) line index where things match up again
    for i, c in enumerate(self.buffer[self.cursori:]):
      x += 1
      if x > self.size[0] and self.wrap:
        x = 1
        if i >= n and self.cursori + i + n in self.linesi:
          end = self.linesi.index(self.cursori + i + n)
          break
        newLinesi.append(self.cursori + i)
      if c == "\n":
        x = 0
        if i >= n and self.cursori + i + 1 + n in self.linesi:
          end = self.linesi.index(self.cursori + i + 1 + n)
          break
        newLinesi.append(self.cursori + i + 1)
    self.linesi[start:end] = newLinesi
    for i in range(start + len(newLinesi), len(self.linesi)):
      self.linesi[i] -= n
    self.cursor = self.getPos(self.cursori)
    self.doScroll()

  # handle a key
  def handle(self, key):
    if key == "right":
      self.cursori = min(len(self.buffer), self.cursori + 1)
      self.cursor = self.getPos(self.cursori)
      self.doScroll()
    elif key == "left":
      self.cursori = max(0, self.cursori - 1)
      self.cursor = self.getPos(self.cursori)
      self.doScroll()
    elif key == "down":
      self.cursor[1] = min(len(self.linesi), self.cursor[1] + 1)
      self.cursori = self.getCursori(self.cursor)
      self.doScroll()
    elif key == "up":
      self.cursor[1] = max(0, self.cursor[1] - 1)
      self.cursori = self.getCursori(self.cursor)
      self.doScroll()
    elif key == "bs":
      if self.cursori == 0:
        return
      self.delete(self.cursori - 1, 1)
    else:
      self.write(key)
