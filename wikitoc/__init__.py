from os import chdir, scandir
import re
import fileinput


"""
Generates table of contents for a wiki
"""

file_exclusion_re: re.Pattern = re.compile(
    r"^\..*$|^_Sidebar\.md$|^_Footer.md$|Home.md"
)
dash_to_space = str.maketrans("-", " ")
underscore_to_space = str.maketrans("_", " ")


def scan_files( root_dir: str ) -> str:

    result: str = "# Table of Contents\n\n"
    tag_tree: dict = {
        "untagged": []
    }

    # get the list of files
    chdir( root_dir )
    files_in_dir = scandir()
    files_to_scan = [
        f.name
        for f in files_in_dir
        if f.is_file() and not file_exclusion_re.match(f.name)
    ]

    with fileinput.input(files_to_scan,
                         openhook=lambda filename, mode: open(filename, mode, errors="replace" )) as f:
        for one_line in f:
            fn = fileinput.filename()
            # assume the file is untagged
            tag_tree["untagged"].append(fn)
            if len(tags_list := _scan_line_for_tags( one_line )) > 0:
                # tag found, remove the file from the list of completely untagged files
                # and add it to one of the tag entries
                tag_tree["untagged"].remove(fn)
                for one_tag in tags_list:
                    _add_filename_to_tag_dict( fn, one_tag, tag_tree )
                fileinput.nextfile()

    result += _render_tag_tree(tag_tree)

    return result


def _scan_line_for_tags( line_to_scan: str ) -> [str]:
    """
    Scan a single file for tags. This is a line that looks like:
    Tags: Tag_One Tag_Two Tag_Three-Sub_Tag_A

    :param: line_to_scan: path to a file to be scanned
    """
    if line_to_scan.startswith( "Tags: " ):
        # return a list of tags, without the initial Tags: indicator
        return line_to_scan.split()[1:]

    else:
        return []


def _add_filename_to_tag_dict( filename: str, tag_seq: str, tag_dict: dict ) -> None:
    """
    Add the filename to the tag dict. The dict structure looks like:
    {
        "untagged": ["file1", "file2", "file3"],
        "tag1: {
            "untagged": ["file4"]
        }
        "tag2": {
            "untagged": []
            "sub-tag3": {
                "untagged": ["file5", "file6"]
            }
        }
        "tag4": {
            "untagged": ["file5"]
        }
    }

    :param filename:
    :param tag_dict:
    """
    current_dict = tag_dict
    for current_level in tag_seq.split("-"):
        current_dict = current_dict.setdefault( current_level, dict() )
    current_dict.setdefault( "untagged", list() ).append(filename)


def _render_tag_tree( tag_tree: dict, level: int = 1 ) -> str:

    result = ""

    for one_filename in tag_tree["untagged"]:
        result += f"[{one_filename.translate(dash_to_space)}]({one_filename})\n\n"

    sub_tags = sorted(tag_tree.keys())
    sub_tags.remove("untagged")
    for one_tag in sub_tags:
        result += f"{'#'*level} {one_tag.translate(underscore_to_space)}\n\n"
        result += _render_tag_tree( tag_tree[one_tag], level+1 )

    return result
