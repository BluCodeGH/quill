import re

def regex(q, e):
  exp = e.prompt("Exp: ")
  while exp is not None:
    found = re.finditer(exp, e.main.text.contents)
    noMatch = True
    for f in found:
      noMatch = False
      e.main.cursori = f.start()
      e.main.selection = [f.start(), f.end()]
      e.main.reflow()
      nexp = e.prompt("Exp: ", exp)
      if nexp != exp:
        exp = nexp
        break
    if noMatch:
      exp = e.prompt("No matches found. Exp: ", exp)
  e.statusbar()
  e.main.selection = [0, 0]
