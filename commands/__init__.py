import pkgutil
import importlib
import inspect

commands = {}

for _, module, _ in pkgutil.walk_packages(__path__, __name__ + "."):
  m = importlib.import_module(module)
  for name, func in inspect.getmembers(m, inspect.isfunction):
    if name[0] != "_":
      commands[name] = func

def get(*args):
  return commands.get(*args)

__all__ = [get]
