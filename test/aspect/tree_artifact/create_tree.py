import logging
import sys
from argparse import ArgumentParser, Namespace
from os import getcwd
from pathlib import Path

logging.basicConfig(format="%(message)s", level=logging.INFO)


def cli() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--tree_root", required=True, type=Path, help="Create source code below this directory.")
    parser.add_argument("--tree_part", choices=["public_headers", "private_headers", "sources"])
    parser.add_argument("--verbose", action="store_true", help="Print debugging output")

    args = parser.parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    return args


def main(args: Namespace) -> int:
    logging.debug(f"Tree root   : '{args.tree_root}'")
    logging.debug(f"mode        : '{args.tree_part}'")
    logging.debug(f"Working dir : '{getcwd()}'")

    args.tree_root.mkdir(parents=True, exist_ok=True)
    if args.tree_part == "public_headers":
        with open(args.tree_root / "tree_lib.h", mode="w", encoding="utf-8") as out:
            out.write("int doTreeThings();\n")
    elif args.tree_part == "private_headers":
        with open(args.tree_root / "tree_impl.h", mode="w", encoding="utf-8") as out:
            out.write("int doPrivateStuff() { return 1337; };\n")
    else:
        with open(args.tree_root / "tree_lib.cc", mode="w", encoding="utf-8") as out:
            out.write(
                '#include "tree_artifact/public_hdrs.h/tree_lib.h"\n'
                '#include "tree_artifact/private_hdrs.h/tree_impl.h"\n'
                '#include "tree_artifact/some_lib.h"\n'
                "int doTreeThings() { return doSomething() + doPrivateStuff(); };\n"
            )

    return 0


if __name__ == "__main__":
    sys.exit(main(cli()))
