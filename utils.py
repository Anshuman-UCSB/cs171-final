import sys
from colorama import init as colorama_init
from colorama import Fore, Back
from colorama import Style
import re

def isDebug():
	return "debug" in sys.argv

TIMEOUT = .5 if isDebug() else 3

colors = [eval(f"Fore.{x.upper()}") for x in ("cyan", "green", "yellow", "blue", "magenta", "white")]

def debug(*args, **kwargs):
	try:
		pid = int(args[0])
	except ValueError:
		pid = -1
	level = kwargs.get("level",1)
	kwargs.pop("level", None)
	if isDebug() and level <= verbosityLevel():
		print(f"{Fore.RED}DEBUG:{Style.RESET_ALL}",Style.DIM+colors[pid],*args, **kwargs,end=f"{Style.RESET_ALL}\n")

def error(*args, **kwargs):
	print(f"{Fore.WHITE}{Back.RED}ERROR:",Fore.WHITE,*args, **kwargs,end=f"{Style.RESET_ALL}\n")

def parseNums(string):
	return list(map(int, re.findall('[0-9]+', string)))

def parseArgs(string):
	string = "(".join(string.split('(')[1:])
	return [x for x in map(lambda x: x.strip(), re.split(r"[\(\),]",string)) if x]


def verbosityLevel():
	last = sys.argv[-1]
	try:
		return int(last)
	except:
		return 0

def log(func):
    argnames = func.__code__.co_varnames[:func.__code__.co_argcount]
    fname = func.__name__
      
    def inner_func(*args, **kwargs):
        print(fname, "(", end = "")
        print(', '.join( '% s = % r' % entry
            for entry in zip(argnames, args[:len(argnames)])), end = ", ")
        print("args =", list(args[len(argnames):]), end = ", ")
        print("kwargs =", kwargs, end = "")
        print(")")
          
    return inner_func