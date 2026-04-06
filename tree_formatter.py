# tree_formatter.py

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
from tree_builder import ProcessTreeBuilder
from models import ProcessInfo
from utils import get_exec_name, visible_len
from constants import (
    CHARSETS,
    GLYPH_STYLES,
    RESET, GRAY, CYAN,
    YELLOW, RED,
    DEFAULT_CPU_THRESHOLD, WHITE
)

# =========================================================
# Class: ProcessTreeFormatter
# =========================================================
class ProcessTreeFormatter:
    """
    Responsible for rendering processes in a hierarchical tree structure.

    This formatter takes a filtered/sorted process list and builds a visual
    tree representation using parent-child relationships.

    Core responsibilities:
    - Build process tree structure via ProcessTreeBuilder
    - Compute subtree CPU usage (including descendants)
    - Sort nodes based on selected criteria
    - Prune irrelevant or low-value branches
    - Render tree using ASCII/UTF-8 branch glyphs
    - Apply optional color formatting

    Features:
    - Subtree CPU aggregation with caching
    - CPU visibility modes (--cpu-all, --cpu-threshold)
    - Depth limiting (--tree-depth)
    - Intelligent branch pruning
    - Stable and safe recursion (loop protection)

    This class operates purely on in-memory data and does not
    interact with the system or modify process state.
    """

    # --------------------------------------------------------------------
    # Method: format
    # --------------------------------------------------------------------
    @staticmethod
    def format(processes: List[ProcessInfo],  all_processes, args, use_color: bool):
        """
        Render the process tree as a list of formatted strings.

        Args:
            processes (List[ProcessInfo]):
                Filtered process list (visible nodes).

            all_processes:
                Full process list used to build complete tree structure.

            args:
                Parsed CLI arguments controlling sorting, depth,
                CPU visibility, and output behavior.

            use_color (bool):
                Enable or disable ANSI color formatting.

        Returns:
            List[str]: Rendered tree lines ready for printing.

        Notes:
            - Tree structure is built from all_processes to preserve hierarchy
            - Only processes in `processes` are considered visible
            - Rendering respects depth limits and pruning rules
        """

        visible_pids = {p.pid for p in processes}

        roots, children = ProcessTreeBuilder.build(all_processes)

        subtree_cache = {}

        # --------------------------------------------------------------------
        # Method: compute_subtree_cpu
        # --------------------------------------------------------------------
        def compute_subtree_cpu(node, visited=None):
            """
            Recursively compute total CPU usage for a node and all descendants.

            Uses memoization (subtree_cache) to avoid redundant calculations.
            """
            if visited is None:
                visited = set()

            if node.pid in visited:
                return 0  # break cycle safely

            visited.add(node.pid)

            if node.pid in subtree_cache:
                return subtree_cache[node.pid]

            total = node.cpu

            for child in children.get(node.pid, []):
                total += compute_subtree_cpu(child, visited.copy())

            subtree_cache[node.pid] = total
            return total

        sort_key_outer = args.sort

        # If sort by command, descend on --bottom
        if sort_key_outer == "cmd":
            reverse = args.bottom  # default ascending, -b reverses
        else:
            reverse = not args.bottom  # default descending, -b flips

        # --------------------------------------------------------------------
        # Method: get_sort_value
        # --------------------------------------------------------------------
        def get_sort_value(p):
            """
            Determine sorting value based on selected key.

            For CPU sorting, subtree CPU is used instead of per-process CPU.
            """
            if sort_key_outer == "cpu":
                return compute_subtree_cpu(p)
            elif sort_key_outer == "mem":
                return p.mem
            elif sort_key_outer == "pid":
                return p.pid
            elif sort_key_outer == "cmd":
                return (p.command or "").lower()
            return compute_subtree_cpu(p)

        if sort_key_outer == "cmd":
            roots = sorted(
                roots,
                key=lambda p: (p.command or "").lower(),
                reverse=reverse
            )
        else:
            roots = sorted(roots, key=get_sort_value, reverse=reverse)

        lines = []
        printed = set()

        # --------------------------------------------------------------------
        # Method: is_boring
        # --------------------------------------------------------------------
        def is_boring(node):
            """
            Identify low-value system processes that should be hidden
            unless they contribute meaningful data to the tree.

            Helps reduce visual noise in large process trees.
            """
            exec_name = get_exec_name(node.command)

            return (
                    node.user == "root"
                    and node.cpu == 0.0
                    and node.mem == 0.0
                    and exec_name not in ("Xorg", "sshd", "init", "login")
            )


        # --------------------------------------------------------------------
        # Method: has_visible_descendant
        # --------------------------------------------------------------------
        def has_visible_descendant(node, visited=None):
            """
            Determine whether a node or any of its descendants
            should be displayed in the tree.

            Prevents rendering of empty or irrelevant branches.
            """
            if visited is None:
                visited = set()

            if node.pid in visited:
                return False

            visited.add(node.pid)

            if node.pid in visible_pids and not is_boring(node):
                return True

            for child in children.get(node.pid, []):
                if has_visible_descendant(child, visited):
                    return True

            return False

        # --------------------------------------------------------------------
        # Method: format_subtree_cpu
        # --------------------------------------------------------------------
        def format_subtree_cpu(value):
            """Format CPU value for display."""
            return f"{value:.1f}%"

        # --------------------------------------------------------------------
        # Method: render
        # --------------------------------------------------------------------
        def render(node, prefix="", is_last=True, visited=None, depth=1):
            """
            Recursively render a process node and its children.

            Handles:
            - Tree glyph construction
            - Depth limiting
            - CPU display logic
            - Color formatting
            - Recursion safety
            """

            if args.tree_depth is not None and depth > args.tree_depth:
                return

            if node.pid in printed:
                return

            printed.add(node.pid)
            if visited is None:
                visited = set()

            # Prevent infinite recursion
            if node.pid in visited:
                return

            visited.add(node.pid)

            charset_key = (args.charset or "utf8").lower().replace("-", "")
            CHARSETS.get(charset_key, CHARSETS["utf8"])

            glyph = GLYPH_STYLES.get(str(args.glyph_style or "1"), GLYPH_STYLES["1"])

            branch = glyph["last"] if is_last else glyph["branch"]

            line_prefix = prefix + (branch if prefix else "")

            pid_str = str(node.pid)
            cmd_str = node.command
            cpu_part = ""

            if use_color:
                pid_str = f"{WHITE}{pid_str}{RESET}"
                cmd_str = f"{RESET}{CYAN}{cmd_str}{RESET}"

            user_str = node.user

            if use_color:
                user_str = f"{YELLOW}{user_str}{RESET}"

            if node.pid in visible_pids:
                cpu_total = compute_subtree_cpu(node)

                # Determine CPU visibility mode
                if args.cpu_all:
                    show_cpu = True

                elif args.cpu_threshold is not None:
                    show_cpu = cpu_total >= args.cpu_threshold

                else:
                    show_cpu = (prefix == "") or cpu_total > DEFAULT_CPU_THRESHOLD

                if show_cpu:
                    cpu_str = format_subtree_cpu(cpu_total)

                    if use_color:
                        if cpu_total >= 80:
                            cpu_str = f"{RED}{cpu_str}{RESET}"
                        elif cpu_total >= 40:
                            cpu_str = f"{YELLOW}{cpu_str}{RESET}"
                        else:
                            cpu_str = f"{GRAY}{cpu_str}{RESET}"

                    cpu_part = f" (CPU: {cpu_str})"

            pipe = glyph["pipe"]
            space = glyph["space"]

            new_prefix = prefix + (space if is_last else pipe)

            sort_key = args.sort

            if sort_key == "cmd":
                children_nodes = sorted(
                    children.get(node.pid, []),
                    key=lambda p: (p.command or "").lower(),
                    reverse=reverse
                )
            else:
                children_nodes = sorted(
                    children.get(node.pid, []),
                    key=get_sort_value,
                    reverse=reverse
                )

            # Filter children to avoid rendering irrelevant branches
            filtered_children = [
                c for c in children_nodes
                if has_visible_descendant(c) and not is_boring(c)
            ]


            is_leaf = len(children.get(node.pid, [])) == 0
            leaf_marker = glyph.get("leaf", "") if is_leaf else ""

            if leaf_marker:
                # attach marker to branch (remove trailing space first)
                line_prefix_clean = line_prefix.rstrip()
                prefix_with_marker = f"{line_prefix_clean}{leaf_marker} "
            else:
                prefix_with_marker = line_prefix

            if use_color:
                prefix_with_marker = f"{WHITE}{prefix_with_marker}{RESET}"

            term_width = shutil.get_terminal_size((120, 20)).columns

            # Build left part
            stat_str = node.stat if hasattr(node, "stat") else "?"

            left_part = (
                f"{prefix_with_marker}"
                f"{pid_str:<4} "
                f"{user_str:<6} "
                f"{stat_str:<1} "
                f"{cpu_part}"
            )

            left_width = visible_len(left_part)
            max_cmd_width = max(0, term_width - left_width)

            # --------------------------------------------------
            # Trim command, preserving color
            # --------------------------------------------------
            if not args.line_wrap:

                if max_cmd_width <= 0:
                    cmd_str = ""

                elif visible_len(cmd_str) > max_cmd_width:

                    visible_count = 0
                    result = ""

                    idx = 0
                    while idx < len(cmd_str) and visible_count < max_cmd_width:
                        char = cmd_str[idx]

                        # Handle ANSI escape sequences
                        if char == "\033":
                            seq = char
                            idx += 1
                            while idx < len(cmd_str) and cmd_str[idx] != "m":
                                seq += cmd_str[idx]
                                idx += 1
                            if idx < len(cmd_str):
                                seq += "m"
                                idx += 1
                            result += seq
                            continue

                        result += char
                        visible_count += 1
                        idx += 1

                    cmd_str = result

            # Final line
            line = f"{left_part}{cmd_str}"
            lines.append(line)

            if args.tree_depth is not None and depth >= args.tree_depth:
                return

            for idx, child in enumerate(filtered_children):

                if child.pid == node.pid:
                    continue

                render(child, new_prefix, idx == len(filtered_children) - 1, visited, depth + 1)

        for i, root in enumerate(roots):
            if has_visible_descendant(root):
                render(root, "", i == len(roots) - 1, None, 1)

        if args.number:
            return lines[:args.number]

        return lines
