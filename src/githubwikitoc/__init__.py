from os import rename, scandir
from os.path import splitext
import re
import fileinput
from typing import List


"""
Generates table of contents for a wiki
"""

# excludes files and folders that start with a dot, like .git or .DS_Store
# also excludes _Sidebar.md, _Footer.md, and Home.md
file_exclusion_re: re.Pattern = re.compile(
    r"^\..*$|^_Sidebar\.md$|^_Footer.md$|Home.md"
)
dash_to_space = str.maketrans("-", " ")
underscore_to_space = str.maketrans("_", " ")


def generate_toc() -> None:
    """
    Generate the Table of Contents and place the text into the Home.md file.
    If the HTML comments <!--start TOC--> and <!--end TOC--> exist then the
    ToC will be inserted between them. Otherwise, the ToC will be placed at
    the start of the file and the comments will be added. Text above the
    start and text below the end will be preserved.
    """

    rename( "Home.md", "Home.md.old" )
    with open( "Home.md", "w" ) as new_home_md:
        with open( "Home.md.old", "r" ) as old_home_md:

            # Read and dump out text before the ToC
            while one_line := old_home_md.readline():
                if one_line == "<!--start TOC-->\n":
                    # We reached the top of the old TOC
                    break
                else:
                    # We haven't reached the top of the old TOC yet so
                    # transfer the old content to the new file.
                    new_home_md.write(one_line)

            if len(one_line) == 0:
                # reached EOF without finding an existing TOC
                # Put the TOC at the beginning of the file, then
                # rewind and put the rest of the old home file's content
                # after that.
                # This is slightly inefficient, but good enough for this purpose
                new_home_md.seek(0)
                new_home_md.write(scan_files())
                old_home_md.seek(0)
                for existing_line in old_home_md:
                    new_home_md.write(existing_line)
                return

            # We found the old TOC, so skip lines until the end of the old TOC
            while one_line := old_home_md.readline():
                if one_line == "<!--end TOC-->\n":
                    break

            # Either we found the old TOC and skipped to the bottom of it
            # or we never found the bottom marker and skipped all of the rest
            # of the file.
            # In either case write the new TOC
            new_home_md.write( scan_files() )

            # Read and dump out text after the ToC
            while one_line := old_home_md.readline():
                new_home_md.write(one_line)


def scan_files() -> str:
    """
    Scan the wiki files and produce a Table of Contents.
    The ToC uses MediaWiki-style links because GitHub Wikis are bugged.

    :return: Markdown-formatted (with MediaWiki-style links) ToC
    """
    result: str = "<!--start TOC-->\n\n# Table of Contents\n\n"
    tag_tree: dict = {
        "untagged": set()
    }

    # get the list of files
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
            tag_tree["untagged"].add(fn)
            if len(tags_list := _scan_line_for_tags( one_line )) > 0:
                # tag found, remove the file from the list of completely untagged files
                # and add it to one of the tag entries
                tag_tree["untagged"].discard(fn)
                for one_tag in tags_list:
                    _add_filename_to_tag_dict( fn, one_tag, tag_tree )
                fileinput.nextfile()

    result += _render_tag_tree(tag_tree) + "<!--end TOC-->\n"

    return result


def _scan_line_for_tags( line_to_scan: str ) -> List[str]:
    """
    Scan a single file for tags. This is a line that looks like:
    Tags: Tag_One Tag_Two Tag_Three-Sub_Tag_A

    :param line_to_scan: path to a file to be scanned
    :return: list of tags in that line
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
        "untagged": {"file1", "file2", "file3"}
        "tag1": {
            "untagged": ["file4"]
        }
        "tag2": {
            "untagged": {}
            "sub-tag3": {
                "untagged": {"file5", "file6"}
            }
        }
        "tag4": {
            "untagged": {"file5"}
        }
    }

    :param filename: name of the file to be added to the tag_dict
    :param tag_seq: list of tags to be added
    :param tag_dict: dictionary where the tags will be added
    """
    current_dict = tag_dict
    for current_level in tag_seq.split("-"):
        current_dict = current_dict.setdefault( current_level, dict() )
    current_dict.setdefault( "untagged", set() ).add(filename)


def _render_tag_tree( tag_tree: dict, level: int = 2 ) -> str:
    """
    Render the tag tree into a string with links to the pages.

    :param tag_tree: dict containing the tags
    :param level: how many #'s to put in front of tag headings
    :return: tag tree rendered as Markdown
    """
    result = ""

    for one_filename in sorted(list(tag_tree["untagged"])):
        # strip off the extension then change dashes to spaces
        # Prefix link with 'wiki/' so that it works right
        # This is a GitHub bug
        stripped_filename = splitext(one_filename)[0]
        munged_filename = stripped_filename.translate(dash_to_space)
        result += f"[{munged_filename}](wiki/{stripped_filename})\n\n"

    sub_tags = sorted(tag_tree.keys())
    sub_tags.remove("untagged")
    for one_tag in sub_tags:
        result += f"{'#'*level} {one_tag.translate(underscore_to_space)}\n\n"
        result += _render_tag_tree( tag_tree[one_tag], level+1 )

    return result
