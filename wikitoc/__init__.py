from os import chdir, walk
from os.path import splitext
from pathlib import PosixPath
import re


"""
Generates table of contents for a wiki
"""

file_exclusion_re : re.Pattern = re.compile(
    r"^\..*$|^_Sidebar\.md$|^_Footer.md$|Home.md"
)


def scan_files( root_dir: str ) -> list:

    result: str = "# Table of Contents\n\n"
    chdir( root_dir )

    for root, dirs, files in walk("."):

        path_segments = PosixPath(root).parts
        if len(path_segments) > 0:
            result += f"{'#'*(len(path_segments)+1)} {path_segments[-1]}\n\n"

        filtered_files = [
            f
            for f in files
            if not file_exclusion_re.match(f)
        ]
        for one_file in filtered_files:
            display_string = one_file.translate(
                str.maketrans("-", " ")
            )
            result += f"[{splitext(display_string)[0]}]({one_file})\n\n"

        dirs_to_remove = [
            d
            for d in dirs
            if d.startswith(".")
        ]

        for one_dir in dirs_to_remove:
            dirs.remove(one_dir)

    return result


