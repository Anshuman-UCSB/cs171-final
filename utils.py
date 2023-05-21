import sys
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

def debug(*args, **kwargs):
	if "debug" in sys.argv:
		print(f"{Fore.RED}DEBUG:{Style.RESET_ALL}",Style.DIM,*args, **kwargs,end=f"{Style.RESET_ALL}\n")