# formatter.py

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

import shutil
from typing import List

# Local imports
from constants import (
    CYAN, GRAY, RED,
    RESET, WHITE, YELLOW,

    MEM_W, PID_W, RSS_W,
    START_W, THR_W, TIME_W,
    USER_W, CPU_W, STAT_W
)
from utils import (
    format_time,
    format_started
)
from models import ProcessInfo

# =========================================================
# Class: ProcessFormatter
# =========================================================
class ProcessFormatter:
    """
    Responsible for formatting process data into a structured
    tabular representation for terminal output.

    This class converts a list of ProcessInfo objects into aligned
    text rows with fixed-width columns, ensuring readability in
    CLI environments.

    Handles:
    - Column layout and alignment
    - Numeric formatting (CPU, memory, RSS, time)
    - Optional ANSI color styling

    Does NOT:
    - Fetch, filter, or sort data
    - Perform any tree-based rendering

    This formatter is used for the standard table (non-tree) view.
    """

    # --------------------------------------------------------------------
    # Method: format
    # --------------------------------------------------------------------
    @staticmethod
    def format(processes: List[ProcessInfo], use_color: bool, args) -> List[str]:


        lines = []
        term_width = shutil.get_terminal_size((120, 20)).columns

        # Format column headers (width)
        header = (
            f"{'PID':<{PID_W}}"
            f"{'USER':<{USER_W}}"
            f"{'STAT':<{STAT_W}}"
            f"{'CPU%':<{CPU_W}}"
            f"{'MEM%':<{MEM_W}}"
            f"{'RSS':<{RSS_W}}"
            f"{'THR':<{THR_W}}"
            f"{'STARTED':<{START_W}}"
            f"{'TIME':<{TIME_W}}"
            f"{'COMMAND'}"
        )

        fixed_width = (
                PID_W +
                USER_W +
                STAT_W +
                CPU_W +
                MEM_W +
                RSS_W +
                THR_W +
                START_W +
                TIME_W
        )

        # Leave some breathing room (1–2 spaces buffer)
        cmd_max_width = max(10, term_width - fixed_width - 2)

        if not args.no_header and not args.raw:
            lines.append("")
            lines.append(header)
            lines.append("-" * len(header))

        # List and format processes (width)
        for p in processes:

            # Hide idle kernel process unless --all
            cmd = p.command.strip().lower().strip("[]")
            if "idle" in p.command.lower():
                print("FILTER CHECK:", p.pid, p.command)
            if not args.all:
                if cmd == "idle":
                    continue

            # Hide internal ps command used for fetch
            cmd = p.command.lower()

            if cmd.startswith("ps ") and "-axo" in cmd:
                continue

            # Raw Mode
            if args.raw:
                lines.append(
                    f"{p.pid} {p.user} {p.cpu:.1f} {p.mem:.1f} {p.command}"
                )
                continue

            # Pre-format values FIRST
            pid_str = f"{p.pid:<{PID_W}}"
            user_str = f"{p.user:<{USER_W}}"
            stat_str = f"{p.stat:<4}"
            cpu_str = f"{p.cpu:.1f}"
            mem_str = f"{p.mem:.1f}"
            rss_str = f"{p.rss_mb:.1f}M"
            thr_str = f"{p.threads}"
            started = format_started(p.started)
            time_str = format_time(p.time)
            cmd_str = p.command

            # Truncate command to avoid terminal wrapping
            if not args.line_wrap and len(cmd_str) > cmd_max_width:
                cmd_str = cmd_str[:cmd_max_width]

            # Apply padding BEFORE color
            pid_str = f"{pid_str:<{PID_W}}"
            user_str = f"{user_str:<{USER_W}}"
            stat_str = f"{stat_str:<{STAT_W}}"
            cpu_str = f"{cpu_str:<{CPU_W}}"
            mem_str = f"{mem_str:<{MEM_W}}"
            rss_str = f"{rss_str:<{RSS_W}}"
            thr_str = f"{thr_str:<{THR_W}}"
            start_str = f"{started:<{START_W}}"
            time_str = f"{time_str:<{TIME_W}}"

            # Apply colors AFTER padding
            if use_color:

                pid_str = f"{WHITE}{pid_str}{RESET}"
                user_str = f"{YELLOW}{user_str}{RESET}"
                stat_str = f"{WHITE}{stat_str}{RESET}"
                # CPU special logic (override base gray)
                if p.cpu >= 80:
                    cpu_str = f"{RED}{cpu_str}{RESET}"
                elif p.cpu >= 40:
                    cpu_str = f"{YELLOW}{cpu_str}{RESET}"
                else:
                    cpu_str = f"{GRAY}{cpu_str}{RESET}"

                mem_str = f"{WHITE}{mem_str}{RESET}"
                rss_str = f"{WHITE}{rss_str}{RESET}"
                thr_str = f"{WHITE}{thr_str}{RESET}"
                start_str = f"{GRAY}{start_str}{RESET}"
                time_str = f"{GRAY}{time_str}{RESET}"
                cmd_str = f"{CYAN}{cmd_str}{RESET}"

            # Final line (NO formatting here anymore!)
            line = (
                f"{pid_str}"
                f"{user_str}"
                f"{stat_str}"
                f"{cpu_str}"
                f"{mem_str}"
                f"{rss_str}"
                f"{thr_str}"
                f"{start_str}"
                f"{time_str}"
                f"{cmd_str}"
            )

            lines.append(line)

        return lines
