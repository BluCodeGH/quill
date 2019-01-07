import os.path

def openf(q, e, f):
  try:
    with open(f) as IF:
      e.main.set(IF.read())
  except FileNotFoundError:
    e.status("Could not find file {}".format(f))
    return
  e.main.cursori = 0
  e.main.update()
  e.meta["file"] = f
  e.meta["name"] = os.path.basename(f)
  q.drawbar()
  e.status("Opened {}".format(f))

def save(q, e):
  f = e.meta.get("file", None)
  if f is None:
    f = e.prompt("Save as: ")
    e.meta["file"] = f
    e.meta["name"] = os.path.basename(f)
  with open(f, "w") as OF:
    OF.write(e.main.text.contents)
  q.drawbar()
  e.status("Saved {}".format(f))

def saveas(q, e, f):
  if f == "":
    f = e.meta.get("file", None)
    if f is None:
      e.status("Unknown filename, could not save.")
      return
  else:
    e.meta["file"] = f
    e.meta["name"] = os.path.basename(f)
  with open(f, "w") as OF:
    OF.write(e.main.text.contents)
  q.drawbar()
  e.status("Saved {}".format(f))
