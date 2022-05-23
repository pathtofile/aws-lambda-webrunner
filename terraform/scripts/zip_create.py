import argparse
from zipfile import ZipFile
from pathlib import PurePath

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Create a ZIP containing a single file")
    parser.add_argument("input_file")
    parser.add_argument("output_zip")
    args = parser.parse_args()

    with ZipFile(args.output_zip, "w") as zipf:
        zipf.write(args.input_file, arcname=PurePath(args.input_file).name)
