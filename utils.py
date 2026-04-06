# utils.py

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

from datetime import datetime
import re
import json
from typing import Optional

# Local imports
from models import ProcessInfo, ProcessNode
from constants import CYAN, RESET

# =========================================================
# Function: format_time
# =========================================================
def format_time(raw_time: str) -> str:
    """
    Convert ps TIME field to HH:MM:SS.
    Handles formats like:
        MM:SS
        H:MM:SS
        M:SS.xx
    """
    if not raw_time:
        return "00:00:00"

    # Remove fractional seconds if present
    raw_time = raw_time.split(".")[0]

    parts = raw_time.split(":")

    try:
        if len(parts) == 2:
            # MM:SS → 00:MM:SS
            minutes, seconds = map(int, parts)
            return f"00:{minutes:02}:{seconds:02}"

        elif len(parts) == 3:
            # H:MM:SS → HH:MM:SS
            hours, minutes, seconds = map(int, parts)
            return f"{hours:02}:{minutes:02}:{seconds:02}"

    except ValueError:
        pass

    return "00:00:00"

# =========================================================
# Function: format_started_time
# =========================================================
def format_started_time(started_str):

    try:
        dt = datetime.strptime(started_str, "%a %b %d %H:%M:%S %Y")
        now = datetime.now()

        if dt.date() == now.date():
            return dt.strftime("%H:%M")
        else:
            return dt.strftime("%a %d")

    except ValueError:
        return started_str


# =========================================================
# Function: format_started
# =========================================================
def format_started(started: str) -> str:
    """
    Format BSD start time into ps-like format:

    - Today → HH:MM
    - Older → Day + Date (Thu 2) OR Month + Date (Apr 2)
    """

    try:
        dt = datetime.strptime(started, "%a %b %d %H:%M:%S %Y")
        now = datetime.now()

        # Same day → show time
        if dt.date() == now.date():
            return dt.strftime("%H:%M")

        # Older → show day + date (NO month)
        return dt.strftime("%a %d")

        # OPTIONAL alternative:
        # return dt.strftime("%b %d")

    except ValueError:
        return started

# =========================================================
# Function: format_time
# =========================================================
ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m')

def visible_len(s: str) -> int:
    return len(ANSI_ESCAPE.sub('', s))


# =========================================================
# Function: get_exec_name
# =========================================================
def get_exec_name(cmd: str) -> str:
    """
    Extract executable name from command string.
    Works for both 'comm' and full 'command'.
    """
    if not cmd:
        return ""
    return cmd.split()[0].split("/")[-1]

# =========================================================
# Function: build_tree_json
# =========================================================
def build_tree_json(roots, children, args):
    """
    Convert process tree into JSON-serializable structure.
    """

    subtree_cache = {}
    printed = set()

    # --------------------------------------------------------------------
    # Method: compute_subtree_cpu
    # --------------------------------------------------------------------
    def compute_subtree_cpu(node, visited):
        if node.pid in visited:
            return 0

        visited.add(node.pid)

        if node.pid in subtree_cache:
            return subtree_cache[node.pid]

        total = node.cpu

        for child in children.get(node.pid, []):
            if child.pid == node.pid:
                continue

            total += compute_subtree_cpu(child, visited.copy())

        subtree_cache[node.pid] = total
        return total

    # --------------------------------------------------------------------
    # Method: build_node
    # --------------------------------------------------------------------
    def build_node(node, depth=1, visited=None) -> Optional[ProcessNode]:
        if visited is None:
            visited = set()

        # GLOBAL[!] protection (like tree renderer)
        if node.pid in printed:
            return None

        printed.add(node.pid)

        # recursion protection
        if node.pid in visited:
            return None

        visited.add(node.pid)

        if args.tree_depth is not None and depth > args.tree_depth:
            return None

        cpu_total = compute_subtree_cpu(node, set())

        node_data: ProcessNode = {
            "pid": node.pid,
            "ppid": node.ppid,
            "user": node.user,
            "command": node.command,
            "cpu": node.cpu,
            "subtree_cpu": cpu_total,
            "mem": node.mem,
            "threads": node.threads,
            "rss_mb": node.rss_mb,
            "started": node.started,
            "time": node.time,
            "children": []
        }

        for child in children.get(node.pid, []):
            if child.pid == node.pid:
                continue  # safety guard

            child_node = build_node(child, depth + 1, visited.copy())
            if child_node:
                node_data["children"].append(child_node)

        return node_data

    return [
        node
        for root in roots
        if root
        for node in [build_node(root, 1, set())]
        if node is not None
    ]


# =========================================================
# Function: load_json_processes
# =========================================================
def load_json_processes(path, args):
    """
    Load process data from a JSON file and convert it into ProcessInfo objects.

    Supports both flat JSON lists and tree-based JSON structures.
    """

    try:
        with open(args.load, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise SystemExit("Error: File not found")
    except json.JSONDecodeError:
        raise SystemExit("Error: Invalid JSON file")
    except Exception as e:
        raise SystemExit(f"Error loading file: {e}")

    if not isinstance(data, list):
        raise SystemExit("Error: Invalid snapshot format")

    if not data:
        raise SystemExit("Error: Snapshot file is empty")

    required_keys = {
        "pid", "ppid", "user", "command",
        "cpu", "mem", "threads"
    }

    for entry in data:
        validate_node(entry, required_keys)

    is_tree = (
            isinstance(data[0], dict)
            and isinstance(data[0].get("children", []), list)
    )

    processes = []

    def walk(node, parent_pid=None):
        if not node:
            return

        pid = node.get("pid")
        ppid = node.get("ppid", parent_pid or 0)

        processes.append(
            ProcessInfo(
                pid=pid,
                ppid=ppid,
                user=node.get("user", ""),
                stat=node.get("stat", "?"),
                cpu=node.get("cpu", 0.0),
                mem=node.get("mem", 0.0),
                rss_mb=node.get("rss_mb", 0.0),
                started=node.get("started", "N/A"),
                time=node.get("time", "N/A"),
                threads=node.get("threads", 0),
                command=node.get("command", "")
            )
        )

        # Only recurse if tree structure exists
        if is_tree:
            for child in node.get("children", []):
                walk(child, pid)

    #
    if is_tree:
        for root in data:
            walk(root)
    else:
        # flat JSON → no recursion
        for item in data:
            walk(item)

    return processes

# =========================================================
# Function: validate_node
# =========================================================
def validate_node(entry, required_keys):
    if not isinstance(entry, dict):
        raise SystemExit("Error: Invalid snapshot structure")

    if not required_keys.issubset(entry.keys()):
        raise SystemExit("Error: Snapshot missing required fields")

    # Validate children recursively
    children = entry.get("children", [])
    if children:
        if not isinstance(children, list):
            raise SystemExit("Error: Invalid children structure")

        for child in children:
            validate_node(child, required_keys)


# =========================================================
# Function: limit_tree_nodes
# =========================================================
def limit_tree_nodes(nodes, limit):
    """
    Limit total number of nodes in a tree structure.
    Traverses depth-first and stops after `limit` nodes.
    """
    count = 0

    def _walk(node_list):
        nonlocal count
        result = []

        for node in node_list:
            if count >= limit:
                break

            count += 1

            new_node = dict(node)
            children = node.get("children", [])

            new_node["children"] = _walk(children)
            result.append(new_node)

        return result

    return _walk(nodes)

# =========================================================
# Function: print_summary
# =========================================================
def print_summary(count, use_color, mode="tree"):
    """
    Print a concise summary of the displayed output.

    This function reports how many entries were rendered in the current
    view (tree or table), providing quick feedback when working with
    large or truncated outputs.

    Args:
        count (int): Number of entries displayed.
        use_color (bool): Enable colored output if True.
        mode (str): Output mode ("tree" or "table") to adjust wording.
    """

    if mode == "tree":
        text = f"\n[Summary] Nodes displayed: {count}\n"
    else:
        text = f"\n[Summary] Processes displayed: {count}\n"

    if use_color:
        text = f"{CYAN}{text}{RESET}"

    print(text)
