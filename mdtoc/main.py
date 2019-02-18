from __future__ import print_function
from __future__ import unicode_literals

import argparse
import os
import pkg_resources
import re
import sys

import requests
from xtermcolor import colorize


def as_link(x):
    """Convert Markdown header string into relative URL."""
    return re.sub(r"[^a-zA-Z0-9-_]", "", x.lower().replace(" ", "-"))


def escape(x):
    """Escape brackets, '['' and ']'."""
    return x.replace("[", "\\[").replace("]", "\\]")


def toc(md_string):
    """Takes a Markdown string, returns TOC string (in Markdown)."""
    toc = []
    for level, header in headers(md_string):
        toc.append(
            "{spaces}* [{header}](#{link})".format(
                spaces="  " * (level - 1),
                header=escape(header),
                link=as_link(header),
            )
        )
    return "\n".join(toc)


def headers(md_string):
    """Takes a Markdown string, returns generator of (level, header) tuples."""
    is_comment_block = False
    for line in md_string.split("\n"):
        if line.startswith("```"):
            is_comment_block = not is_comment_block
        if is_comment_block:
            continue
        header = re.match(r"^(#+)(.*)", line)
        if header:
            level = len(header.group(1))
            header = header.group(2).strip()
            yield level, header


def modify_and_write(path):
    with open(path) as fp:
        markdown = fp.read()
        table_of_contents = toc(markdown)

    toc_re = re.compile(
        r"^<\!---toc start-->(.*?)<\!---toc end-->$",
        flags=re.DOTALL|re.MULTILINE
    )
    new_markdown, replacements = toc_re.subn(
        "<!---toc start-->\n\n{}\n\n<!---toc end-->".format(table_of_contents),
        markdown,
    )

    with open(path, "w") as fp:
        fp.write(new_markdown)


def get_links(md_string):
    def line_col(position):
        l, c = 1, 1
        for idx, char in enumerate(md_string):
            if idx == position:
                break
            elif char in {"\r", "\n"}:
                l, c = l + 1, 1
            else:
                l, c = l, c + 1
        return (l, c)

    results = []
    for m in re.finditer(r"\[([^\[\]]*)\]\((.*?)\)", md_string, re.M):
        line, col = line_col(m.start(1))
        results.append((m.group(1), m.group(2), line, col))
    return results


_description = """
Generates table of contents for Markdown files

The algorithm searches for the text blocks
between the delimiters:

<!---toc start--->
... anything ...
<!---toc end--->

The contents of the block are then replaced
by a table of contents.
"""


def cli():
    parser = argparse.ArgumentParser(
        description=_description,
        epilog="Created by Scott Frazer (https://github.com/scottfrazer)",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=str(pkg_resources.get_distribution("mdtoc")),
    )
    parser.add_argument(
        "--check-links",
        action="store_true",
        help="Find all hyperlinks and ensure that \nthey point to something valid",  # noqa
    )
    parser.add_argument("markdown_file")

    cli = parser.parse_args()
    cli.markdown_file = os.path.expanduser(cli.markdown_file)
    if not os.path.isfile(cli.markdown_file):
        sys.exit("File not found: {}".format(cli.markdown_file))

    modify_and_write(cli.markdown_file)

    if cli.check_links:
        with open(cli.markdown_file) as fp:
            contents = fp.read()

        valid_http_fragments = [
            "#" + as_link(h) for (l, h) in headers(contents)
        ]
        for text, link, line, col in get_links(contents):
            valid = "unrecognized link type"
            if link.startswith("#"):
                if link not in valid_http_fragments:
                    valid = colorize("INVALID", ansi=1)
                else:
                    valid = colorize("VALID", ansi=2)
            elif link.startswith("http://") or link.startswith("https://"):
                r = requests.get(link)
                valid = "Response: {}".format(r.status_code)
            print(
                "Checking {line}:{col} [{text}]({link}) --> {valid} ".format(
                    text=colorize(text, ansi=3),
                    link=colorize(link, ansi=4),
                    line=line,
                    col=col,
                    valid=valid,
                )
            )
