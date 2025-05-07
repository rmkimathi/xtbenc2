# XTB Encoder
xtbenc is a gui for ffmpeg. It combines the beauty of GUI with the power of commandline for geeks!

_"(Fast Forward MPEG) An open source multimedia project for working with audio and video. Based on the "libavcodec" A/V codec library and "libavformat" multiplexing framework, FFmpeg is a command-line utility that can encode and decode a variety of media formats. Started in 2000 by Fabrice Bellard, FFmpeg can be compiled to run under all popular operating systems. ..." - Encyclopedia_

![Options](images/xtbenc-01.png)

# Resources
In Ubuntu if you get an error similar to: ImportError: No module named tkinter then you need to install tkinter.
```
sudo apt install python3-tk
sudo apt install python3-testresources

sudo apt install python3-venv

python -m venv venv

~/venv/bin/pip install PySimpleGUI-4-foss

~/venv/bin/pip install pyinstaller

~/venv/bin/python xtbenc.py


pip3 install PySimpleGUI-4-foss

pip3 install pyinstaller


# Ubuntu
~/venv/bin/pyinstaller --add-data="_internal/presets:presets" xtbenc.py


# Windows
pyinstaller --icon=xtbenc.ico --add-data="_internal/presets:presets" xtbenc.py
```

# PySimpleGUI-4-foss (Open-Source Fork)
As of April 2025, installing PySimpleGUI version 4 on Ubuntu has become challenging due to significant changes in the project's distribution and licensing:
⚠️ Important Changes to PySimpleGUI

Version 5 Transition: PySimpleGUI has transitioned to version 5, which now requires a license for use. While it's free for hobbyists, commercial use necessitates a paid license.

Discussions on Python.org

Removal of Version 4 from PyPI: All version 4 releases have been removed from the Python Package Index (PyPI), making them unavailable for direct installation via pip.

Reddit

✅ Alternative: Install PySimpleGUI-4-foss (Open-Source Fork)

To continue using the last open-source version of PySimpleGUI, you can install the PySimpleGUI-4-foss package, which is a community-maintained fork of version 4.60.4.1

# Usage
ffmpeg.exe and ffprobe.exe should be in env path or drop your static binaries in the same folder as xtbenc. ffmpeg arguments can be typed in directly in the "Extra Options" combo or permanently added by editing the csv files in the presets folder.

[Download binaries ...](https://github.com/rmkimathi/xtbenc2/releases)

# Reference
[PySimpleGUI](https://github.com/PySimpleGUI/PySimpleGUI)

[Shlex](https://docs.python.org/3.6/library/shlex.html)

[Subprocess](https://docs.python.org/3.6/library/subprocess.html)

[CSV](https://docs.python.org/3.6/library/csv.html)

[Live loop](https://github.com/fabianlee/blogcode/tree/master/python)

[FFmpeg](https://www.ffmpeg.org/download.html)
