import logging
import term
from buffer import Buffer
logging.basicConfig(filename='quill.log', level=logging.DEBUG, format="%(message)s")

class Tab:
  def __init__(self, pos, size, wrap=True):
    self.main = Buffer(pos, (size[0], size[1] - 1), wrap)
    self.status = Buffer((pos[0], pos[1] + size[1] - 1), (size[0], 1), False)

  def handle(self, key):
    self.main.handle(key)
    self.updateStatus()

  def updateStatus(self):
    self.status.set(str(self.main.getCursor(self.main.cursori)))
    self.main.focusCursor()

def main():
  logging.info("Starting quill.")
  term.color(0, 7)
  term.clear()
  term.color(7, 0)
  T = Tab((0, 0), term.size, True)
  k = term.getkey()
  while k != "^C":
    T.handle(k)
    k = term.getkey()
  logging.info("Exiting.")

term.wrapper(main)
