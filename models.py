# models.py

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

from dataclasses import dataclass
from typing import List, TypedDict

# =========================================================
# Data class: ProcessInfo
# =========================================================
@dataclass
class ProcessInfo:
    """
    Data model representing a single process entry.

    This class acts as a structured container for process information
    collected from the system (via `ps`). Each instance corresponds
    to one process and contains both raw and pre-processed attributes
    used throughout the application.

    Fields:
        pid (int):
            Process ID.

        ppid (int):
            Parent Process ID. Used for building the process tree.

        user (str):
            Username that owns the process.

        cpu (float):
            CPU usage percentage for this process.
            Note: On BSD systems, this may exceed 100% on multicore systems.

        mem (float):
            Memory usage percentage.

        rss_mb (float):
            Resident Set Size in megabytes (physical memory usage).

        started (str):
            Full start time string as returned by `ps`
            (e.g. "Thu Apr  2 17:06:03 2026", later formatted for display).


        time (str):
            Total CPU time consumed by the process
            (raw format from `ps`, later formatted for display).

        threads (int):
            Number of threads associated with the process.

        command (str):
            Command or executable name of the process.

    Role in the system:
        - Produced by ProcessFetcher
        - Filtered by ProcessFilter
        - Sorted by ProcessSorter
        - Consumed by Formatter and TreeFormatter

    This class does NOT contain logic — it is strictly a data container.
    """
    pid: int
    ppid: int
    user: str
    stat: str
    cpu: float
    mem: float
    rss_mb: float
    started: str
    time: str
    threads: int
    command: str


# =========================================================
# TypedDict: ProcessNode
# =========================================================
class ProcessNode(TypedDict):
    pid: int
    ppid: int
    user: str
    command: str
    cpu: float
    subtree_cpu: float
    mem: float
    threads: int
    started: str
    time: str
    rss_mb: float
    children: List["ProcessNode"]

