# See AUTHORS.

# Copyright (c) 2018-2020, D.J. Sutherland
# Copyright (c) 2024-2025  cryslith

# This program is free software: you can redistribute it and/or modify
# it under the terms of version 3 of the GNU General Public License as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import argparse
import io
import os
import re
import subprocess
import tarfile

from .strip import strip_comments

class LatexmkException(Exception):
    def __init__(self, message, base_error=None):
        super(LatexmkException, self).__init__(message)
        self.base_error = base_error

def get_deps(base_name, latexmk="latexmk", skip_bbl=False):
    print('Running latexmk...')
    args = [
        latexmk,
        "-silent",
        "-pdf",
        "-deps",
        base_name,
    ]
    try:
        output = subprocess.check_output(args, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        msg = (
            "Build failed with code {}\n".format(e.returncode)
            + "Called {}\n".format(args)
            + "\nOutput was:\n"
            + e.output.decode()
        )
        raise LatexmkException(msg, base_error=e)
    latexmk_deps = extract_dependencies(output.decode())
    bbl_deps = [x for x in [base_name + '.bbl'] if not skip_bbl and os.path.exists(x)]
    return latexmk_deps + bbl_deps

def extract_dependencies(output):
    deps = re.search(
        r"^#===Dependents(?:, and related info,)? for (?:.*):\n(?:.*):\\$((?:.|\n)*)^#===End dependents for (?:.*):$",
        output,
        re.MULTILINE,
    ).group(1).split('\n')
    deps = (x.strip() for x in deps if x.strip())
    return [x[:-1] if x.endswith('\\') else x for x in deps]

def process(deps, out_tar, args):
    pkg_re = '/' + '|'.join(re.escape(p) for p in args.packages) + '/' if args.packages else None

    for dep in deps:
        if args.exclude_files and any(re.match(excl, dep) for excl in args.exclude_files):
            continue
        if os.path.isabs(dep):
            if pkg_re and pkg_re.search(dep):
                print(dep)
                out_tar.add(dep, arcname=os.path.basename(dep))
        elif dep.endswith(".tex") and args.strip_comments:
            print(dep)
            with open(dep) as f, io.BytesIO() as g:
                tarinfo = tarfile.TarInfo(name=dep)
                content = f.read()
                new_content = strip_comments(content)
                g.write(new_content.encode('utf-8'))
                tarinfo.size = g.tell()
                g.seek(0)
                out_tar.addfile(tarinfo=tarinfo, fileobj=g)
        else:
            print(dep)
            out_tar.add(dep)

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "base_name",
        help="Name of the main tex file.",
    )
    parser.add_argument(
        "-o", "--output", "--dest", default="arxiv.tar.gz", help="Output path [default: %(default)s]."
    )
    parser.add_argument(
        "-f", "--overwrite",
        action="store_true",
        help="Overwrite output file without warning.",
    )
    parser.add_argument(
        "--include-package",
        "-p",
        action="append",
        dest="packages",
        help=(
            "Include a system package in the collection if used; can pass more "
            "than once."
        ),
    )
    parser.add_argument(
        "--latexmk",
        default="latexmk",
        help="Path to the latexmk command [default: %(default)s].",
    )
    parser.add_argument(
        '--skip-bbl',
        action='store_true',
        help="Don't include .bbl file if it exists",
    )
    g = parser.add_mutually_exclusive_group()
    g.add_argument(
        "--strip-comments",
        action="store_true",
        default=True,
        help="Strip comments from all .tex files (by default).",
    )
    g.add_argument(
        "--no-strip-comments",
        action="store_false",
        dest="strip_comments",
        help="Don't strip comments from any .tex files.",
    )

    parser.add_argument(
        "--exclude-files",
        metavar="REGEX",
        action='append',
        help="File paths matching REGEX won't actually be added to the tar; "
        "uses re.match (i.e. should match from the start, relative to the base "
        "directory), and applies to output filenames. Can pass multiple times.",
    )

    args = parser.parse_args()

    if args.base_name.endswith(".tex"):
        args.base_name = args.base_name[:-4]

    return args


def main():
    args = parse_args()

    deps = get_deps(args.base_name, latexmk=args.latexmk, skip_bbl=args.skip_bbl)

    if (
            not args.overwrite and
            os.path.exists(args.output) and
            not input(f'Output file {args.output} already exists, overwrite? [y/N] ').lower().startswith('y')
    ):
        return
    with tarfile.open(args.output, mode="w:gz") as t:
        process(deps, t, args)
    print(f'Output written to {args.output}.')
