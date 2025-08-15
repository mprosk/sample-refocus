import argparse
import subprocess
from pathlib import Path
from typing import List


def get_file_list(target_path: Path) -> List[Path]:
    """
    Recursively iterates through all files in the given Path
    and returns a list of all paths that are a file
    """
    def walk_file_tree(path: Path) -> list:
        if not path.is_dir():
            return []
        files = []
        for file_path in path.iterdir():
            if file_path.is_file():
                files.append(file_path)
            elif file_path.is_dir():
                files.extend(walk_file_tree(file_path))
            else:
                print(file_path, "is neither a file nor a directory...")
        return files

    print("Generating file list for", target_path)
    file_list = walk_file_tree(target_path)
    print(len(file_list), "total files found")
    return file_list


def main(source: str, output: str, rate: int):
    source_root = Path(source)
    output_root = Path(output)
    print("Source:", source_root)
    print("Output:", output_root)

    # Get the list of files in the source directory
    file_list = get_file_list(source_root)

    # Create the output directory if it does not exist
    output_root.mkdir(parents=True, exist_ok=True)

    error_list = []

    for source_file in file_list:

        output_file = output_root / source_file.relative_to(source_root).parent / (source_file.stem + ".wav")
        output_file.parent.mkdir(parents=True, exist_ok=True)

        if output_file.exists():
            print(f"Skipping existing file {output_file}")
            continue

        try:
            subprocess.run(
                ['ffmpeg', '-i', str(source_file), '-ar', str(rate), '-sample_fmt', 's16', str(output_file)],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as ex:
            print("ERROR:", source_file, "-->", output_file)
            print(str(ex))
            error_list.append(source_file)
        else:
            print(source_file, "-->", output_file)

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
    parser.add_argument(
        '--rate',
        type=int,
        default=48000,
        help="set the output audio rate"
    )
    args = parser.parse_args()
    main(args.source, args.output, args.rate)
