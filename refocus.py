import argparse
import shutil
import subprocess
from pathlib import Path

import util


def get_new_filename(source_dir: Path, source_file: Path, output_dir: Path, convert: bool = False) -> Path:
    """Generates the fully resolved and cleaned output file name"""

    ext = ".mp3"
    if convert: ext = ".wav"

    # Remove non-mp3 suffixes
    tokens = source_file.name.split('.')
    i = tokens.index("mp3")
    filename = ".".join(tokens[:i])

    # Remove preceding non-alphanumeric characters
    while not filename[0].isalnum():
        filename = filename[1:]

    # Handle a blank filename
    if not filename: filename = "_"

    # Generate the output path relative to the source path
    output_path = output_dir / source_file.relative_to(source_dir).parent
    target_path = output_path / (filename + ext)

    # Check if file exists and append numbers to prevent overwrites
    i = 1
    while target_path.exists():
        target_path = output_path / f"{filename}_{i}{ext}"
        i += 1

    # Check for overly long filenames
    if len(target_path.name) > 255:
        print("WARNING: long filename:", source_file, "-->", target_path)

    return target_path


def main(mode: str, source: str, output: str):
    source_root = Path(source)
    output_root = Path(output)
    print("Source:", source_root)
    print("Output:", output_root)

    # Get the list of files in the source directory
    file_list = util.get_file_list(source_root)

    # Create the output directory if it does not exist
    output_root.mkdir(parents=True, exist_ok=True)

    error_list = []

    with open(output_root / "refocus.log", mode='w') as log:
        for i, source_file in enumerate(file_list):
            target_file = get_new_filename(source_root, source_file, output_root)
            target_file.parent.mkdir(parents=True, exist_ok=True)
            exception = None

            if mode == "copy":
                try:
                    shutil.copy2(source_file, target_file)
                except Exception as e:
                    exception = e

            elif mode == "convert":
                try:
                    subprocess.run(
                        ['ffmpeg', '-i', str(source_file), '-ar', '48000', '-sample_fmt', 's16', str(target_file)],
                        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except subprocess.CalledProcessError as ex:
                    exception = e

            # Check if we had errors
            if exception is not None:
                error_list.append(source_file)
                print("ERROR:", source_file, "-->", target_file)
                print(str(exception))
            else:
                log.write(f"{source_file} --> {target_file}\n")

            # Print progress indicator
            if i % 100 == 0:
                print(i, "of", len(file_list), f"({round(i / len(file_list) * 100)}%)")

    if error_list:
        print("Errors were encountered on the following files:")
        for p in error_list:
            print(p)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'mode',
        type=str,
        choices=['copy', 'convert'],
        help="action to perform")
    parser.add_argument(
        'source',
        type=str,
        help="root directory containing the files to process")
    parser.add_argument(
        'output',
        type=str,
        help="target directory to output processed files")
    args = parser.parse_args()
    main(args.mode, args.source, args.output)
