import commands

class Shortcuts:
  def __init__(self, fname, quill, editor):
    self.dict = {}
    self.quill = quill
    self.editor = editor
    with open(fname) as f:
      for line in f.readlines():
        if line.strip(" \t\n") == "":
          continue
        keys, fname = line.strip(" \t\n").split(" ", 1)
        func = commands.get(fname, None)
        if func is None:
          raise KeyError("Function '{}'' not defined.".format(fname))
        self.add(keys.split("+"), func)

  def add(self, keys, val, d=None):
    if d is None:
      d = self.dict
    if len(keys) == 1:
      if keys[0] in d:
        if isinstance(d[keys[0]], dict):
          d[keys[0]][None] = val
        else:
          raise KeyError("Redefining shortcut for function '{}'.".format(val))
      else:
        d[keys[0]] = val
    else:
      if keys[0] in d:
        if not isinstance(d[keys[0]], dict):
          f = d[keys[0]]
          d[keys[0]] = {None:f}
      else:
        d[keys[0]] = {}
      self.add(keys[1:], val, d[keys[0]])

  def go(self, keys, d=None, args=None):
    d = d or self.dict
    args = args or [self.quill, self.editor]
    if len(keys) == 1:
      if keys[0] in d:
        n = d[keys[0]]
        if callable(n):
          res = n(*args)
          if res:
            return True
        elif None in n:
          res = n[None](*args)
          if res:
            return True
        else:
          return True
      elif "{}" in d:
        args.append(keys[0])
        n = d["{}"]
        if callable(n):
          res = n(*args)
          if res:
            return True
        elif None in n:
          res = n[None](*args)
          if res:
            return True
        else:
          return True
      else:
        return None
    else:
      if keys[0] in d:
        return self.go(keys[1:], d[keys[0]], args)
      elif "{}" in d:
        args.append(keys[0])
        return self.go(keys[1:], d["{}"], args)
      else:
        return None
    return False
