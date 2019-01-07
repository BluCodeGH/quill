def newtab(q, e):
  q.newtab()
  e.statusbar()

def closetab(q, e):
  q.closetab()
  e.statusbar()

def switchtab(q, e, i):
  if i != "":
    try:
      if int(i) < len(q.editors):
        q.switchtab(int(i))
        e.statusbar()
      else:
        raise ValueError
    except ValueError:
      e.status("Invalid tab identifier {}".format(i))
  else:
    q.switchtab((q.focus + 1) % len(q.editors))
    e.statusbar()
