"""cx_Freeze setup script"""
import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [Executable(
    "main.pyw",
    icon="icon.ico",
    targetName="YT Downloader",
    base=base
)]

options = {"build_exe": {"include_files": ["icon.ico"]}}

setup(
    name="YT Downloader",
    description="GUI application for downloading video",
    options=options,
    executables=executables,
)
