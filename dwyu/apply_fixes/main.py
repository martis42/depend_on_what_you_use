import logging
import sys

from dwyu.apply_fixes.apply_fixes import main
from dwyu.apply_fixes.cli import cli

logging.basicConfig(format="%(message)s", level=logging.INFO)

if __name__ == "__main__":
    sys.exit(main(cli()))
