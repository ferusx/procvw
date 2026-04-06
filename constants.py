# constants.py

"""
    procvw is a process viewer developed for FreeBSD.
    Copyright (C) 2026  Markus Johnsson a.k.a. FerusX.Swe
    All rights reserved.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    For the GNU General Public License, see <https://www.gnu.org/licenses/>.
"""


# Header widths constants
PID_W = 7
USER_W = 10
STAT_W = 5
CPU_W = 7
MEM_W = 6
RSS_W = 8
THR_W = 5
TIME_W = 10
START_W = 10

# Colors constants
GRAY = "\033[38;2;168;168;168m"
WHITE = "\033[97m"
CYAN = "\033[96m"
RED = "\033[91m"
YELLOW = '\033[38;2;200;180;60m'
RESET = "\033[0m"

# CPU Threshold constant
DEFAULT_CPU_THRESHOLD = 1.0

# Charset
CHARSETS = {
    "utf8": {
        "branch": "├─ ",
        "last": "└─ ",
        "pipe": "│  ",
        "space": "   ",
    },
    "ascii": {
        "branch": "|- ",
        "last": "`- ",
        "pipe": "|  ",
        "space": "   ",
    }
}

# Some glyph styles for the tree mode
GLYPH_STYLES = {
    "1": {  # classic
        "branch": "├─ ",
        "last": "└─ ",
        "pipe": "│  ",
        "space": "   ",
    },
    "2": {  # ascii
        "branch": "|- ",
        "last": "`- ",
        "pipe": "|  ",
        "space": "   ",
    },
    "3": {  # fancy
        "branch": "├─ ",
        "last": "└─ ",
        "leaf": "◆ ",
        "pipe": "│   ",
        "space": "    ",
    }
}
