def quit(q, e):
  q.running = False

def echo(q, e, *args):
  e.main.write(",".join(args))
  e.status("Echoed: " + ",".join(args))

def run(q, e, py):
  e.status(eval(py))

def nul(q, e):
  pass
