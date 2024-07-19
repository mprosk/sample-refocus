import argparse
from pathlib import Path

import util


def get_token_dict(file_list):
    token_dict = dict()
    for i, source_file in enumerate(file_list):
        filename = source_file.name.split(".mp3")[0]
        filename = filename.replace("-", "_")
        filename = filename.replace(".", "_")
        for token in filename.split("_"):
            if not token: continue
            token = token.lower()
            if token in token_dict:
                token_dict[token] += 1
            else:
                token_dict[token] = 1
    return token_dict


def main(source: str):
    source_root = Path(source)
    file_list = util.get_file_list(source_root)
    return get_token_dict(file_list)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'source',
        type=str,
        help="root directory containing the files to process")
    args = parser.parse_args()
    main(args.source)
