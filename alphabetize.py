import argparse
import shutil
from pathlib import Path

import util


def main(source: str, output: str):
    source_dir = Path(source)
    output_dir = Path(output)
    print("Source:", source_dir)
    print("Output:", output_dir)

    # Get the list of files in the source directory
    file_list = util.get_file_list(source_dir)

    # Create the output directory if it does not exist
    output_dir.mkdir(parents=True, exist_ok=True)

    for file_path in file_list:
        output_file = output_dir / file_path.name[0].upper() / file_path.name
        output_file.parent.mkdir(parents=True, exist_ok=True)
        print(file_path, "-->", output_file)
        shutil.move(file_path, output_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'source',
        type=str,
        help="root directory containing the files to process")
    parser.add_argument(
        'output',
        type=str,
        help="target directory to output processed files")
    args = parser.parse_args()
    main(args.source, args.output)
