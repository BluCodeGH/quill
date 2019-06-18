import logging
import term
import text
logging.basicConfig(filename='quill.log', level=logging.DEBUG, format="%(message)s")
logging.info("Starting quill.")

def main():
  term.color(0, 7)
  term.clear()
  term.color(7, 0)
  T = text.Text((0, 0), term.size, True)
  k = term.getkey()
  while k != "^C":
    T.handle(k)
    k = term.getkey()

term.wrapper(main)
