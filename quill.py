import term

def main():
  term.clear()
  k = term.getkey()
  while k != "^C":
    term.write(k)
    k = term.getkey()

term.wrapper(main)
