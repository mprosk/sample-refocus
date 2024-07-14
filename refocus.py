import argparse
import shutil
import subprocess
from pathlib import Path

import util


def process_file(source_dir: Path, source_file: Path, output_dir: Path):
    filename = clean_filename(source_file.name)
    output_path = output_dir / source_file.relative_to(source_dir).parent
    copy_path = output_path / (filename + ".wav")

    # Append numbers to prevent overwriting other files
    i = 1
    while copy_path.exists():
        copy_path = output_path / f"{filename}_{i}.wav"
        i += 1

    # Check for overly long filenames
    if len(copy_path.name) > 255:
        print("WARNING: long filename:", source_file, "-->", copy_path)

    # print(source_file, "-->", copy_path)
    copy_path.parent.mkdir(parents=True, exist_ok=True)
    # shutil.copy2(source_file, copy_path)
    try:
        subprocess.run(['ffmpeg', '-i', str(source_file), '-ar', '48000', '-sample_fmt', 's16', str(copy_path)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as ex:
        print("ERROR:", source_file, "-->", copy_path)
        print(str(ex))
        return None
    return copy_path


def clean_filename(filename: str) -> str:

    # Remove non-mp3 suffixes
    tokens = filename.split('.')
    i = tokens.index("mp3")
    filename = ".".join(tokens[:i])

    # Remove preceding non-alphanumeric characters
    while not filename[0].isalnum():
        filename = filename[1:]

    # Handle a blank filename
    if not filename:
        return "_"

    return filename


def main(source: str, output: str):
    source_path = Path(source)
    output_path = Path(output)
    print("Source:", source_path)
    print("Output:", output_path)

    # Get the list of files in the source directory
    file_list = util.get_file_list(source_path)

    # Create the output directory if it does not exist
    output_path.mkdir(parents=True, exist_ok=True)

    error_list = []

    with open(output_path / "refocus.log", mode='w') as log:
        for i, file_path in enumerate(file_list):
            resolved_path = process_file(source_path, file_path, output_path)
            if resolved_path is not None:
                log.write(f"{file_path} --> {resolved_path}\n")
            else:
                error_list.append(file_path)
            if i % 100 == 0:
                print(i, "of", len(file_list), f"({round(i / len(file_list) * 100)}%)")

    if error_list:
        print("Errors were encountered on the following files:")
        for p in error_list:
            print(p)


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
