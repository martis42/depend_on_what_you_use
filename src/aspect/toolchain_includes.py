import json
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

# TODO logging and verbose arg

def cli() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        "--include_directories",
        required=True,
        metavar="PATH",
        type=Path,
        nargs="*",
        help="TBD",
    )
    parser.add_argument(
        "--toolchain_files",
        required=True,
        metavar="FILE",
        type=Path,
        nargs="*",
        help="TBD",
    )
    parser.add_argument(
        "--output",
        required=True,
        metavar="FILE",
        type=Path,
        help="TBD",
    )
    return parser.parse_args()


def main(args: Namespace) -> int:
    all_files = []
    for ip in args.include_directories:
        all_files.extend([str(f.relative_to(ip)) for f in ip.glob("**/*")])

    for tf in args.toolchain_files:
        if tf.suffix in [".h", ".hh", ".hpp"]:
            all_files.append(str(tf))
        elif not str(tf.name).startswith(".") and tf.suffix == "" and tf.parent.name != "bin":
            # There are files without any suffix for the C++ standard includes (e.g. 'vector'). However, while we want to include them, we do not want hidden support files or tool binaries
            all_files.append(str(tf))


    # ensure no duplicate entries
    all_files = list(set(all_files))

    print("#########")
    print(f"Found: {len(all_files)}")
    print("#########")

    with args.output.open(mode="wt", encoding="utf-8") as output:
        json.dump(all_files, output)

    return 0


if __name__ == "__main__":
    cli_args = cli()
    sys.exit(main(cli_args))
