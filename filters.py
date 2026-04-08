# filters.py

# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 Markus Johnsson

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
            filters = [f.lower() for f in args.cmd_filter]

            result = [
                p for p in result
                if any(f in (p.command or "").lower() for f in filters)
            ]

        # Hide kernel processes (Default)
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

        def stat_key(p):
            """
            Map a process STAT value to a sortable priority.

            The STAT field from ps(1) contains a primary process state along
            with optional modifier flags (e.g. "S", "Ss", "R+", "I<").

            For sorting purposes, only the primary state (first character) is
            considered. This function translates that state into a numeric
            priority to ensure consistent and meaningful ordering.

            Priority order (default):

                R   Running processes
                D   Uninterruptible sleep (I/O wait)
                S   Sleeping
                I   Idle / kernel threads
                T   Stopped or traced
                Z   Zombie processes

            Any unrecognized or uncommon states are placed at the end.

            This mapping aligns table sorting with tree mode behavior, ensuring
            consistent output across different views.

            Args:
                p (ProcessInfo):
                    Process entry containing the STAT field.

            Returns:
                int:
                    Numeric priority representing the process state.
                    Lower values indicate higher priority in ascending order.

            Note:
                Modifier flags (e.g. "+", "s", "<") are ignored for sorting.
            """
            state = (p.stat or "")[:1]

            priority = {
                "R": 0,
                "D": 1,
                "S": 2,
                "I": 3,
                "T": 4,
                "Z": 5
            }

            return priority.get(state, 99)

        # Map CLI sort options to corresponding process attributes
        key_map = {
            "stat": stat_key,
            "cpu": lambda p: p.cpu,
            "mem": lambda p: p.mem,
            "pid": lambda p: p.pid,
            "rss": lambda p: p.rss_mb,
            "thr": lambda p: p.threads,
            "cmd": lambda p: (p.comm or "").lower()
        }

        # Select sorting function (default: CPU)
        key_func = key_map.get(args.sort, key_map["cpu"])

        # Sort behavior
        # - cmd is alphabetical (ascending by default)
        # - numeric/categorical priority sorts (cpu, mem, pid, stat, etc.)
        #   are descending by default
        if args.sort in "cmd":
            reverse = args.bottom  # allow reversing for command
        else:
            # Reverse determines descending vs ascending order
            reverse = not args.bottom  # default: descending

        return sorted(processes, key=key_func, reverse=reverse)
