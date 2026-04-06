# fetcher.py

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

import subprocess
from typing import List

# Local imports
from models import ProcessInfo

# =========================================================
# Class: ProcessFetcher
# =========================================================
class ProcessFetcher:
    """
    Responsible for retrieving process data from the system.

    Uses the BSD `ps` command to collect raw process information
    and converts each row into a structured ProcessInfo object.

    NOTE: This is the ONLY component that interacts with the system.
    """

    # --------------------------------------------------------------------
    # Method: fetch
    # --------------------------------------------------------------------
    @staticmethod
    def fetch(args) -> List[ProcessInfo]:
        """
        Executes the `ps` command and parses its output into ProcessInfo objects.

        Returns:
            List[ProcessInfo]: List of all processes retrieved from the system

        Notes:
            - Relies on fixed column positions from the `ps` output
            - Uses manual splitting to reconstruct multi-field values
              such as start time and command
            - Silently skips malformed lines
        """

        if args.show_path:
            cmd = "ps -ww -axo pid,ppid,user,state,%cpu,%mem,rss,lstart,time,nlwp,command"
        else:
            cmd = "ps -ww -axo pid,ppid,user,state,%cpu,%mem,rss,lstart,time,nlwp,comm"

        output = subprocess.check_output(cmd, shell=True, text=True)

        # We skip the header line
        lines = output.strip().split("\n")[1:]

        processes = []

        for line in lines:
            try:
                # Split into columns (lstart and command require reconstruction)
                parts = line.split()

                pid = int(parts[0])
                ppid = int(parts[1])
                user = parts[2]
                stat = parts[3]
                cpu = float(parts[4])
                mem = float(parts[5])
                rss_kb = int(parts[6])
                rss_mb = rss_kb / 1024

                # lstart = 5 fields: "Thu Apr  2 17:06:03 2026"
                started = " ".join(parts[7:11])

                time = parts[12]
                threads = int(parts[13])

                # command may contain spaces → join remaining parts
                command = " ".join(parts[14:])

                processes.append(
                    ProcessInfo(
                        pid=pid,
                        ppid=ppid,
                        user=user,
                        stat=stat,
                        cpu=cpu,
                        mem=mem,
                        rss_mb=rss_mb,
                        started=started,
                        time=time,
                        threads=threads,
                        command=command
                    )
                )

            except ValueError:
                # Skip malformed or unexpected lines safely
                continue

        return processes

