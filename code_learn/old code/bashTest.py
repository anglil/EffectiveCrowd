from fileProcessing import *
import subprocess

# f2 ="eval2.py"
# script = ["""
# 	f="$1"
# 	gzip <"$f"> "$f".gz
# """]


# runScript(script)
subprocess.call("./ttt.sh hello", shell=True)