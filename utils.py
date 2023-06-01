import sys
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
import re

def debug(*args, **kwargs):
	if isDebug():
		print(f"{Fore.RED}DEBUG:{Style.RESET_ALL}",Style.DIM,*args, **kwargs,end=f"{Style.RESET_ALL}\n")

def parseNums(string):
	return list(map(int, re.findall('[0-9]+', string)))

def parseArgs(string):
	string = "(".join(string.split('(')[1:])
	return [x for x in map(lambda x: x.strip(), re.split(r"[\(\),]",string)) if x]

def isDebug():
	return "debug" in sys.argv