import logging
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

logging.basicConfig(format="%(message)s", level=logging.INFO)
log = logging.getLogger(__name__)


def cli() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--tree_root", required=True, type=Path, help="Create source code below this directory.")
    parser.add_argument("--tree_part", choices=["public_headers", "private_headers", "sources"])
    parser.add_argument("--verbose", action="store_true", help="Print debugging output")

    args = parser.parse_args()
    if args.verbose:
        log.setLevel(logging.DEBUG)

    return args


def main(args: Namespace) -> int:
    log.debug(f"Tree root   : '{args.tree_root}'")
    log.debug(f"mode        : '{args.tree_part}'")
    log.debug(f"Working dir : '{Path.cwd()}'")

    args.tree_root.mkdir(parents=True, exist_ok=True)
    if args.tree_part == "public_headers":
        with args.tree_root.joinpath("tree_lib.h").open(mode="w", encoding="utf-8") as out:
            out.write("int doTreeThings();\n")
    elif args.tree_part == "private_headers":
        with args.tree_root.joinpath("tree_impl.h").open(mode="w", encoding="utf-8") as out:
            out.write("int doPrivateStuff() { return 1337; };\n")
    else:
        with args.tree_root.joinpath("tree_lib.cc").open(mode="w", encoding="utf-8") as out:
            out.write(
                '#include "tree_artifact/public_hdrs.h/tree_lib.h"\n'
                '#include "tree_artifact/private_hdrs.h/tree_impl.h"\n'
                '#include "tree_artifact/some_lib.h"\n'
                "int doTreeThings() { return doSomething() + doPrivateStuff(); };\n"
            )

    return 0


if __name__ == "__main__":
    sys.exit(main(cli()))
