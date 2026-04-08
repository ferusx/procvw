# formatter.py

# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 Markus Johnsson

import shutil
from typing import List

# Local imports
from constants import (
    CYAN, GRAY, RED,
    RESET, WHITE, YELLOW, GREEN,

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
    Formats process data into a clean, aligned table for terminal output.

    This class takes a list of ProcessInfo objects and turns them into
    fixed-width rows designed to be easy to scan in a CLI environment.
    The goal is simple: present useful information clearly, without
    distractions or surprises.

    It is responsible for shaping the final look of the default view,
    handling everything from column alignment to subtle visual cues
    like color and spacing.

    Responsibilities:
        - Define column layout and alignment
        - Format numeric values (CPU, memory, RSS, time)
        - Apply optional ANSI color styling
        - Respect display-related flags (wrapping, headers, etc.)

    Boundaries:
        - Does NOT fetch, filter, or sort data
        - Does NOT construct or render process trees
        - Assumes all input is already prepared for display

    Context:

        This formatter powers the standard table view — the first thing
        most users see when running procvw. Because of that, it aims to
        feel familiar, stable, and consistent with traditional UNIX tools
        like ps and top.
    """

    # --------------------------------------------------------------------
    # Method: format
    # --------------------------------------------------------------------
    @staticmethod
    def format(processes: List[ProcessInfo], use_color: bool, args) -> List[str]:
        """
        Format a list of processes into aligned table rows.

        This method transforms ProcessInfo objects into a visual
        representation suitable for terminal output. It handles layout,
        truncation, and optional color styling while respecting user flags.

        Flow:

            1. Determine terminal width
                Used to dynamically size the COMMAND column.

            2. Build header (optional)
                Skipped when --no-header or --raw is used.

            3. Iterate over processes
                - Apply internal filtering (idle/system noise)
                - Handle raw output mode (bypasses formatting)
                - Prepare and align all fields

            4. Width-aware truncation
                COMMAND field is truncated only when necessary,
                based on actual rendered width (excluding colors).

            5. Apply color (optional)
                ANSI colors are added after alignment to avoid
                breaking width calculations.

            6. Assemble final lines
                Fully formatted rows are appended to output.

        Args:
            processes (List[ProcessInfo]):
                Processes to format.

            use_color (bool):
                Whether ANSI color styling should be applied.

            args:
                Parsed CLI arguments controlling formatting behavior.

        Returns:
            List[str]:
                Fully formatted lines ready for printing.

        Notes:

            - Padding is always applied before color to keep alignment stable.
            - Width calculations are performed on uncolored text to avoid
              ANSI escape sequence interference.
            - The COMMAND column adapts to terminal width unless
              --line-wrap is enabled.
        """


        lines = []
        term_width = shutil.get_terminal_size((120, 20)).columns
        # Fallback ensures sane width in non-interactive environments (e.g. pipes/SSH)

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

        # Add a spacing buffer between columns (This is VERY important)
        column_spacing = 2  # simulate visual spacing
        total_spacing = column_spacing * 9  # 9 columns before COMMAND

        real_fixed_width = fixed_width + total_spacing

        if not args.no_header and not args.raw:
            lines.append("")
            lines.append(header)
            lines.append("-" * len(header))

        # List and format processes (width)
        for p in processes:

            # Filter out the idle kernel process unless explicitly requested
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

            # Raw mode bypasses all formatting for simple, script-friendly output
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
            if args.show_path:
                cmd_str = p.command
            else:
                cmd_str = p.comm

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

            # Build the line without COMMAND first to measure available width accurately
            base_line = (
                f"{pid_str}"
                f"{user_str}"
                f"{stat_str}"
                f"{cpu_str:<{CPU_W}}"
                f"{mem_str:<{MEM_W}}"
                f"{rss_str:<{RSS_W}}"
                f"{thr_str:<{THR_W}}"
                f"{start_str}"
                f"{time_str}"
            )

            # Remaining width determines how much of COMMAND can be shown
            remaining_width = term_width - len(base_line)

            if not args.line_wrap and remaining_width > 0:
                cmd_str = cmd_str[:remaining_width]

            # Apply colors AFTER padding to preserve column alignment
            if use_color:

                pid_str = f"{WHITE}{pid_str}{RESET}"
                user_str = f"{GREEN}{user_str}{RESET}"
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
