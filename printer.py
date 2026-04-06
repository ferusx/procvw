# printer.py

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

from typing import List

# =========================================================
# Class: ProcessPrinter
# =========================================================
class ProcessPrinter:
    """
    Responsible for outputting formatted lines to the terminal.

    This is the final stage in the processing pipeline, taking already
    formatted text and sending it to standard output.
    """

    # --------------------------------------------------------------------
    # Method: print
    # --------------------------------------------------------------------
    @staticmethod
    def print(lines: List[str]):
        """
        Print each line to standard output.

        Args:
            lines (List[str]):
                Formatted lines produced by a formatter.
        """
        for line in lines:
            print(line)

