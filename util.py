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
