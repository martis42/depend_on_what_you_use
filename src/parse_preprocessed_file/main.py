import json
import re
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path


def cli() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        "--input",
        required=True,
        metavar="FILE",
        type=Path,
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


#def impl():


def main(args: Namespace) -> int:
    """
    Preprocessor output doc https://gcc.gnu.org/onlinedocs/cpp/Preprocessor-Output.html
    """
    includes = []

    with args.input.open(mode="rt", encoding="utf-8") as input:
        first_line = input.readline().strip()
        file_under_inspection = first_line.split("# 0 ")[1]
        file_under_inspection_marker = f"{file_under_inspection} 2"

        #print(f"DBG_1 '{first_line}'")
        #print(f"DBG_2 '{file_under_inspection}'")
        #print(f"DBG_3 '{file_under_inspection_marker}'")
        
        # skip header part
        header_line = input.readline()
        while file_under_inspection not in header_line:
            header_line = input.readline()

        inside_included_content = False
        for line in input.readlines():
            #print(f"LINE '{line.strip()}'")
            
            if not line.startswith("#"):
                continue

            if inside_included_content and file_under_inspection_marker in line:
                # We reached the end of content placed by an include
                inside_included_content = False
                continue
            
            if not inside_included_content:
                # Is there a 'find first' function?
                matches = re.findall('"(.+)" 1', line)
                #print(matches)
                if len(matches) == 1:
                    # We descend into another section of code added trough an include
                    inside_included_content = True
                    includes.append(matches[0])
                    continue

                if len(matches) > 1:
                    raise RuntimeError("TBD")

    result = {
        "file": file_under_inspection.replace('"', ""),
        "includes": list(set(includes)),
    }

    print("------------")
    print(result)
    print("------------")

    # print("----------")
    # import os
    # print(os.getcwd())
    # print(os.listdir("."))

    #target_dir = args.output.parent
    #print(f"TARGET_D '{target_dir}'")
    #target_dir.mkdir(parents=True, exist_ok=True)
    with args.output.open(mode="wt", encoding="utf-8") as output:
        # Only store unique appearances of includes
        json.dump(result, output)

    return 0


if __name__ == "__main__":
    cli_args = cli()
    sys.exit(main(cli_args))
