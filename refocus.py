import argparse
import shutil
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
        print("Walking", path.as_posix())
        for file_path in path.iterdir():
            if file_path.is_file():
                files.append(file_path)
            elif file_path.is_dir():
                files.extend(walk_file_tree(file_path))
            else:
                print(file_path, "is neither a file nor a directory...")
        print(len(files), "files found")
        return files

    print("Generating file list for", target_path.as_posix())
    file_list = walk_file_tree(target_path)
    print(len(file_list), "total files found")
    return file_list


def process_file(source_dir: Path, source_file: Path, output_dir: Path) -> Path:
    filename = clean_filename(source_file.name)
    output_path = output_dir / source_file.relative_to(source_dir).parent
    copy_path = output_path / (filename + ".wav")

    # Append numbers to prevent overwriting other files
    i = 1
    while copy_path.exists():
        copy_path = output_path / f"{filename}_{i}.wav"
        i += 1

    print(source_file, "-->", copy_path)
    copy_path.parent.mkdir(parents=True, exist_ok=True)
    # shutil.copy2(source_file, copy_path)
    subprocess.run(['ffmpeg', '-i', str(source_file), '-ar', '48000', '-sample_fmt', 's16', str(copy_path)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return copy_path


def clean_filename(filename: str) -> str:

    # Remove non-mp3 suffixes
    tokens = filename.split('.')
    i = tokens.index("mp3")
    filename = ".".join(tokens[:i])

    # Remove preceding underscores
    while filename.startswith('_'):
        filename= filename[1:]

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
    file_list = get_file_list(source_path)

    # Create the output directory if it does not exist
    output_path.mkdir(parents=True, exist_ok=True)

    with open(output_path / "refocus.log", mode='w') as log:
        for i, file_path in enumerate(file_list):
            resolved_path = process_file(source_path, file_path, output_path)
            log.write(f"{file_path} --> {resolved_path}\n")
            if i % 100 == 0:
                print(i, "of", len(file_list), f"({round(i / len(file_list) * 100)}%)")


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
