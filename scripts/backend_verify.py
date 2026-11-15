#!/usr/bin/env python3
"""Compatibility entry point; the installed command is backend-verify."""

import sys

from backend_standard.runner import main

if __name__ == "__main__":
    sys.exit(main())
