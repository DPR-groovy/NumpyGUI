from setuptools import setup
import py2exe
import sys
import matplotlib
sys.setrecursionlimit(5000)

includes = ['sip', 'PyQt5.Qt', 'matplotlib.pyplot', 'numpy', 'matplotlib.backends.backend_qt5agg']

datafiles = [("platforms", ["C:\\Users\\username\\Anaconda2\\pkgs\\qt5-5.6.2-vc9hc26998b_12\\Library\\plugins\\platforms\\qwindows.dll"]),
             ("", [r"c:\windows\system32\MSVCP100.dll", r"c:\windows\system32\MSVCR100.dll"])] + matplotlib.get_py2exe_datafiles()
             
setup(console=[{"script":"example.py"}], options={"py2exe":{"includes":includes}}, data_files=datafiles)
