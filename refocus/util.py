import re
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
        print("Walking", path)
        for file_path in path.iterdir():
            if file_path.is_file():
                files.append(file_path)
            elif file_path.is_dir():
                files.extend(walk_file_tree(file_path))
            else:
                print(file_path, "is neither a file nor a directory...")
        print(len(files), "files found")
        return files

    print("Generating file list for", target_path)
    file_list = walk_file_tree(target_path)
    print(len(file_list), "total files found")
    return file_list


def clean_filename(filename: str) -> str:
    # Remove non-mp3 suffixes
    filename = filename[:filename.rindex(".mp3")]

    # Remove leading non-alphanumeric characters
    filename = re.sub(r'^[\W_]+', '', filename)

    # Remove trailing non-alphanumeric characters
    filename = re.sub(r'[\W_]+$', '', filename)

    # Replace separators with underscores
    filename = filename.replace('.', '_')
    filename = filename.replace('-', '_')

    # Delete duplicated underscores
    filename = re.sub(r'_{2,}', '_', filename)

    # Handle a blank filename
    if not filename:
        return '_'

    return filename

