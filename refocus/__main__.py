import argparse
import shutil
import subprocess
from pathlib import Path

from refocus import util


def get_new_filename(source_dir: Path, source_file: Path, output_dir: Path, convert: bool = False) -> Path:
    """Generates the fully resolved and cleaned output file name"""
    ext = ".mp3"
    if convert: ext = ".wav"

    filename = util.clean_filename(source_file.name)

    # Generate the output path relative to the source path
    output_path = output_dir / source_file.relative_to(source_dir).parent
    target_path = output_path / (filename + ext)

    # Check if file exists and append numbers to prevent overwrites
    i = 1
    while target_path.exists():
        target_path = output_path / f"{filename}_{i}{ext}"
        i += 1

    return target_path


def main(mode: str, source: str, output: str, rename: bool, rate: int):
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

            if rename:
                # Clean up the file name
                try:
                    target_file = get_new_filename(source_root, source_file, output_root, convert=(mode == "convert"))
                except OSError as ex:
                    print(ex)
                    print(source_file)
                    continue
            else:
                # Don't clean up the file name, just make it relative to the output dir
                target_file = output_root / source_file.relative_to(source_root).parent / source_file.name

            target_file.parent.mkdir(parents=True, exist_ok=True)
            exception = None

            match mode:
                case "dry":
                    pass

                case "touch":
                    try:
                        target_file.touch()
                    except Exception as ex:
                        exception = ex

                case "copy":
                    try:
                        shutil.copy2(source_file, target_file)
                    except Exception as ex:
                        exception = ex

                case "convert":
                    try:
                        subprocess.run(
                            ['ffmpeg', '-i', str(source_file), '-ar', str(rate), '-sample_fmt', 's16', str(target_file)],
                            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    except subprocess.CalledProcessError as ex:
                        exception = ex

            # Check if we had errors
            if exception is not None:
                error_list.append(source_file)
                print("ERROR:", source_file, "-->", target_file)
                print(str(exception))
            else:
                log.write(f"{source_file.relative_to(source_root)} --> {target_file.relative_to(output_root)}\n")

            # Print progress indicator
            if i % 100 == 0:
                pass
                print(i, "of", len(file_list), f"({round(i / len(file_list) * 100)}%)")

    if error_list:
        print("Errors were encountered on the following files:")
        for p in error_list:
            print(p)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="refocus")
    parser.add_argument(
        'mode',
        type=str,
        choices=['copy', 'convert', 'touch', 'dry'],
        help="action to perform")
    parser.add_argument(
        'source',
        type=str,
        help="root directory containing the files to process")
    parser.add_argument(
        'output',
        type=str,
        help="target directory to output processed files")
    parser.add_argument(
        '--rename',
        action='store_true',
        help="applies the name cleanup to the files if set")
    parser.add_argument(
        '--rate',
        type=int,
        default=48000,
        help="sample rate of the output WAV files. Default 48000. Only applies if mode='convert'")
    args = parser.parse_args()
    main(args.mode, args.source, args.output, args.rename, args.rate)
