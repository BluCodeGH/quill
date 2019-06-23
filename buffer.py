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
    self.cursori = 0 # reflected position of the cursor
    self.linesi = []
    self.redisplay()
    logging.info("Started buffer at %d, %d", *pos)

  def redisplay(self):
    start = self.scroll[1]
    end = self.scroll[1] + self.size[1]
    for i, (s, e) in enumerate(zip(([0] + self.linesi)[start:end], (self.linesi + [len(self.buffer)])[start:end])):
      term.move(self.pos[0], self.pos[1] + i)
      s += self.scroll[0]
      e = max(min(e, s + self.size[0]), s)
      for c in self.buffer[s:e]:
        if c != "\n":
          term.write(c)
        else:
          term.write(" ")
      term.write(" " * (self.size[0] - e + s))
      #logging.debug("i {} s {} e {}".format(i, s, e))
    complete = len((self.linesi + [len(self.buffer)])[start:end])
    for i in range(self.size[1] - complete):
     term.move(self.pos[0], self.pos[1] + i + complete)
     term.write(" " * self.size[0])

  def getCursori(self, coords):
    s = ([0] + self.linesi)[coords[1]]
    e = (self.linesi + [len(self.buffer) + 1])[coords[1]]
    cursori = s
    cursori += min(coords[0], e - s - 1)
    #logging.debug("coords: {}, i: {}".format(coords, cursori))
    return cursori

  def getCursor(self, cursori):
    cursor = [None, None]
    for i, l in enumerate(self.linesi + [len(self.buffer) + 1]):
      if cursori < l:
        cursor[1] = i
        cursor[0] = cursori - ([0] + self.linesi)[i]
        break
    #logging.debug("i:{}, coords:{}".format(cursori, cursor))
    return cursor

  def doScroll(self, c):
    if c[0] - self.scroll[0] >= self.size[0] - self.border[0] + 1 and not self.wrap:
      self.scroll[0] = c[0] - self.size[0] + self.border[0]
    if c[0] - self.scroll[0] <= self.border[0] and not self.wrap:
      self.scroll[0] = max(c[0] - self.border[0], 0)
    if c[1] - self.scroll[1] >= self.size[1] - self.border[1]:
      self.scroll[1] = c[1] - self.size[1] + self.border[1] + 1
    if c[1] - self.scroll[1] <= self.border[1]:
      self.scroll[1] = max(c[1] - self.border[1], 0)

  def update(self):
    c = self.getCursor(self.cursori)
    self.doScroll(c)
    self.redisplay()
    term.move(self.pos[0] + c[0] - self.scroll[0], self.pos[1] + c[1] - self.scroll[1])

  def focusCursor(self):
    c = self.getCursor(self.cursori)
    term.move(self.pos[0] + c[0] - self.scroll[0], self.pos[1] + c[1] - self.scroll[1])

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
        if i >= len(text) and self.cursori + i - len(text) in self.linesi:
          end = self.linesi.index(self.cursori + i - len(text))
          break
        newLinesi.append(self.cursori + i)
      if c == "\n":
        x = 0
        if i >= len(text) and self.cursori + i + 1 - len(text) in self.linesi:
          end = self.linesi.index(self.cursori + i + 1 - len(text))
          break
        newLinesi.append(self.cursori + i + 1)
    self.linesi[start:end] = newLinesi
    for i in range(start + len(newLinesi), len(self.linesi)):
      self.linesi[i] += len(text)
    self.cursori += len(text)
    self.cursor = self.getCursor(self.cursori)

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
    self.cursor = self.getCursor(self.cursori)
    self.update()

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
    self.cursor = self.getCursor(self.cursori)

  def handle(self, key):
    if key == "right":
      self.cursori = min(len(self.buffer), self.cursori + 1)
      self.cursor = self.getCursor(self.cursori)
    elif key == "left":
      self.cursori = max(0, self.cursori - 1)
      self.cursor = self.getCursor(self.cursori)
    elif key == "down":
      self.cursor[1] = min(len(self.linesi), self.cursor[1] + 1)
      self.cursori = self.getCursori(self.cursor)
    elif key == "up":
      self.cursor[1] = max(0, self.cursor[1] - 1)
      self.cursori = self.getCursori(self.cursor)
    elif key == "bs":
      if self.cursori == 0:
        return
      self.delete(self.cursori - 1, 1)
    else:
      self.write(key)
    self.update()
