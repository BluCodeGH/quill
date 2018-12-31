import curses
import editor

def main(term):
  e = editor.Editor(term)

curses.wrapper(main)
