# filters.py

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
from models import ProcessInfo

# =========================================================
# Class: ProcessFilter
# =========================================================
class ProcessFilter:
    """
    Responsible for filtering process data based on user-provided criteria.

    Applies optional filters such as:
    - User ownership
    - Specific PID
    - Command substring matching

    This stage operates on already fetched data and does not modify
    the original list structure beyond filtering.
    """

    # --------------------------------------------------------------------
    # Method: apply
    # --------------------------------------------------------------------
    @staticmethod
    def apply(processes: List[ProcessInfo], args) -> List[ProcessInfo]:
        """
        Filter a list of ProcessInfo objects according to CLI arguments.

        Args:
            processes (List[ProcessInfo]):
                The full list of processes to filter.

            args:
                Parsed command-line arguments containing optional filters.

        Returns:
            List[ProcessInfo]: Filtered list of processes

        Notes:
            - Filters are applied sequentially (user → pid → command)
            - Each filter reduces the current result set
            - String matching for command is case-insensitive
        """

        result = processes

        # User
        if args.user:
            result = [p for p in result if p.user == args.user]

        # PID
        if args.pid:
            result = [p for p in result if p.pid == args.pid]

        # Filter
        if args.cmd_filter:
            result = [p for p in result if args.cmd_filter.lower() in p.command.lower()]

        # ---------------------------------------
        # Hide kernel processes (Default)
        # ---------------------------------------
        if not args.all:
            result = [
                p for p in result
                if p.pid != 0 and p.command not in ("kernel", "idle")
            ]

        return result

# =========================================================
# Class: ProcessSorter
# =========================================================
class ProcessSorter:
    """
    Responsible for ordering processes based on user-defined criteria.

    Supports sorting by: (default → descending)
    - CPU usage
    - Memory usage
    - Process ID
    - Resident Set Size in megabytes (physical memory usage).
    - Threads
    - Command (default → ascending, in lower-case)

    Sorting direction can be reversed using the -b, --bottom flag.
    """

    # --------------------------------------------------------------------
    # Method: apply
    # --------------------------------------------------------------------
    @staticmethod
    def apply(processes: List[ProcessInfo], args) -> List[ProcessInfo]:
        """
        Sort a list of ProcessInfo objects according to CLI arguments.

        Args:
            processes (List[ProcessInfo]):
                The list of processes to sort.

            args:
                Parsed command-line arguments containing sorting preferences.

        Returns:
            List[ProcessInfo]: A sorted list of processes

        Notes:
            - Default sorting is by CPU (descending)
            - -b, --bottom reverses the sort order (ascending)
            - Sorting is stable and uses Python's built-in sorted()
        """

        # Map CLI sort options to corresponding process attributes
        key_map = {
            "cpu": lambda p: p.cpu,
            "mem": lambda p: p.mem,
            "pid": lambda p: p.pid,
            "rss": lambda p: p.rss_mb,
            "thr": lambda p: p.threads,
            "cmd": lambda p: (p.command or "").lower()
        }

        # Select sorting function (default: CPU)
        key_func = key_map.get(args.sort, key_map["cpu"])

        # Sort commands in ascending order
        if args.sort == "cmd":
            reverse = args.bottom  # allow reversing for command
        else:
            # Reverse determines descending vs ascending order
            reverse = not args.bottom  # default: descending

        return sorted(processes, key=key_func, reverse=reverse)
