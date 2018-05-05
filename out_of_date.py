#!/usr/bin/env python
"""Command-line interface to out-of-date library"""

import sys

from e_out_of_date.command import main


if __name__ == '__main__':
    main(sys.argv[1:])
