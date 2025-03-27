import argparse
import re

def strip_comments(content):
    return re.sub(r'((?:^|[^\\\n])(?:\\\\)*)%.*(\n?)', r"\1%\2", content, flags=re.MULTILINE)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    args = parser.parse_args()
    with open(args.file) as f:
        print(strip_comments(f.read()), end='')
