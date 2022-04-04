import sys
from cx_Freeze import setup, Executable
from asyncio import events
import PySimpleGUI as sg
import configparser
import requests
import pandas as pd
import datetime


# Dependencies are automatically detected, but it might need fine tuning.
# "packages": ["os"] is used as example only
build_exe_options = {"packages": 
    [
    'pandas',
    'configparser',
    'xlrd',
    'requests',
    'asyncio',
    'PySimpleGUI'
    ],
    'includes':['tkinter'],
    'include_files': ['config.ini', 'icon.ico']
}

# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"
    

setup(
    name = "CalcTax",
    version = "0.1",
    description = "Calculadora de importacao",
    options = {"build_exe": build_exe_options},
    executables = [Executable("app.py", base=base, icon='icon.ico')]
)