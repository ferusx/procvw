# printer.py

# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 Markus Johnsson

from typing import List

# =========================================================
# Class: ProcessPrinter
# =========================================================
class ProcessPrinter:
    """
    Output handler for procvw.

    This class represents the final stage in the processing pipeline,
    responsible for emitting fully formatted lines to standard output.

    It performs no formatting or transformation — all input is assumed
    to be ready for display.
    """

    # --------------------------------------------------------------------
    # Method: print
    # --------------------------------------------------------------------
    @staticmethod
    def print(lines: List[str]):
        """
        Write formatted output lines to standard output.

        Args:
            lines (List[str]):
                Pre-formatted lines produced by a formatter.

        Notes:
            - Each line is printed as-is, preserving alignment,
              color codes, and layout.
            - This method intentionally avoids any additional
              processing to keep output behavior predictable.
        """
        for line in lines:
            print(line)

