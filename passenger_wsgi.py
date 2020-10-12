import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from src.app import application as applicationfn

application = applicationfn(False)