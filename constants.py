# constants.py

# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 Markus Johnsson

# ---------------------------------------------------------------------
# Column Width Constants
# ---------------------------------------------------------------------
#
# These constants define the fixed-width layout of the table output.
# Each value represents the number of characters allocated to a column.
#
# The goal is to:
#   - Ensure consistent alignment across all rows
#   - Prevent shifting when values change in length
#   - Maintain readability in typical terminal widths
#
# NOTE:
#   - These widths are tuned for standard terminal sizes (~80–120 columns)
#   - The COMMAND column is dynamic and consumes remaining space
#   - Adjust carefully — small changes ripple through the entire layout
#

PID_W   = 7   # Process ID
USER_W  = 10  # Username (owner of process)
STAT_W  = 5   # Process state (e.g. R, S, I+, etc.)
CPU_W   = 7   # CPU usage percentage
MEM_W   = 6   # Memory usage percentage
RSS_W   = 8   # Resident Set Size (in MB)
THR_W   = 5   # Number of threads
TIME_W  = 10  # Total CPU time used
START_W = 10  # Process start time (formatted)

# ---------------------------------------------------------------------
# ANSI Color Constants
# ---------------------------------------------------------------------
#
# These constants define the ANSI escape sequences used for colorizing
# terminal output. They are applied selectively to enhance readability
# without overwhelming the user.
#
# Design goals:
#   - Maintain clarity across different terminals and color profiles
#   - Use restrained, meaningful color (not decoration)
#   - Ensure graceful fallback when colors are not supported
#
# Notes:
#   - Colors are only applied when the --color flag is enabled
#   - Different terminals may render colors differently (especially GRAY)
#   - Values are chosen from widely supported 8/16-color ANSI palette
#
# Usage:
#   Wrap strings as: f"{COLOR}{text}{RESET}"
#

GRAY   = "\033[37m"  # Subtle/secondary information (timestamps, low CPU)
WHITE  = "\033[97m"  # Neutral/default foreground (PID, STAT)
CYAN   = "\033[96m"  # Command names (primary visual anchor)
RED    = "\033[91m"  # High CPU usage / critical attention
YELLOW = "\033[33m"  # Medium CPU usage (warning level)
GREEN  = "\033[32m"  # User column (identity / ownership)
RESET  = "\033[0m"   # Reset formatting to terminal default

# ---------------------------------------------------------------------
# CPU Threshold Constant
# ---------------------------------------------------------------------
#
# Default threshold used to determine whether subtree CPU usage should
# be displayed in tree mode when no explicit flags are provided.
#
# Behavior:
#   - Nodes with subtree CPU above this value will show CPU usage
#   - Nodes below this threshold will hide CPU info (unless --cpu-all)
#
# Purpose:
#   - Reduce visual noise in large trees
#   - Highlight only meaningful CPU activity by default
#
# Notes:
#   - Overridden by:
#       --cpu-all        → always show CPU
#       --cpu-threshold  → user-defined threshold
#

DEFAULT_CPU_THRESHOLD = 1.0  # Minimum CPU (%) required to display subtree usage

# ---------------------------------------------------------------------
# Tree Glyph Styles
# ---------------------------------------------------------------------
#
# Defines visual styles for rendering the process tree structure.
# Each style controls how branches, connectors, and optional markers
# appear in tree mode.
#
# Styles:
#
#   "1" → Classic (default)
#          Clean UTF-8 box-drawing style, similar to `tree` or `pstree`
#
#   "2" → ASCII
#          Compatible fallback for terminals without Unicode support
#
#   "3" → Fancy
#          Enhanced visual style with a leaf marker for terminal nodes
#
# Elements:
#
#   branch → Connector for intermediate child nodes
#   last   → Connector for the final child in a branch
#   pipe   → Vertical continuation for nested levels
#   space  → Padding where no pipe is drawn
#   leaf   → Optional marker for leaf nodes (style-dependent)
#
# Notes:
#
#   - Selected via the --glyph-style flag
#   - Defaults to style "1" if not specified
#   - Styles may override spacing for visual alignment
#   - "leaf" is optional and only used if defined
#
GLYPH_STYLES = {
    "1": {  # classic
        "branch": "├─ ",
        "last": "└─ ",
        "pipe": "│  ",
        "space": "   ",
    },
    "2": {  # ascii
        "branch": "|- ",
        "last": "`- ",
        "pipe": "|  ",
        "space": "   ",
    },
    "3": {  # fancy
        "branch": "├─ ",
        "last": "└─ ",
        "leaf": "◆ ",
        "pipe": "│   ",
        "space": "    ",
    }
}
