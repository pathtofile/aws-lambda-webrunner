import os
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Delete a file in an OS-agnostic way")
    parser.add_argument("input_file")
    args = parser.parse_args()

    if os.path.exists(args.input_file):
        os.unlink(args.input_file)
