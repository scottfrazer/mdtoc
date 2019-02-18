# -*- coding: utf-8 -*-
"""Generate generate table of contents within Markdown (.md) files."""

# Steps:
#
# 1. Open .md doc for reading; get the doc as a Python str
# 2. Build a generator of (level: int, header: str) for the found headers
# 3. Format & indent the found headers using []() Markdown style
# 4. Replace '<!---toc start-->', '<!---toc end-->', and text in between
#    with the str result from (3.)
# 5. Overwrite the input file with the result

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import os
import re

import requests
from xtermcolor import colorize


TOC_PAT = re.compile(
    r"[ \t]*<\!---toc start-->(.*?)<\!---toc end-->[ \t]*",
    flags=re.DOTALL | re.M
)

# Pattern needs to be careful for URLs containing parentheses,
# nested within the actual Markdown link's parentheses.
# I.e.
# [Text here](https://www.cool.com/this(-is-a)-link.html)
MD_LINK_PAT = re.compile(
    r"\[([^\[\]]+)\]"  # Brackets containing non-bracket characters
    r"\((([^\s)(]|\([^\s)(]*\))*)\)",  # Outer parentheses
    re.M
)

# A Markdown "atx-style" header
HEADER_PAT = re.compile(r"^(#+)(.*)")


class MarkdownError(Exception):
    """Markdown formatted incorrectly."""


def as_link(x):
    """Convert Markdown header string into relative URL."""

    return re.sub(
        r"[^-\w\s]",
        "",
        re.sub(r"\s+", "-", x.lower()),
        flags=re.U  # Python 2
    )


def escape(x):
    """Escape brackets, '['' and ']'."""
    return x.replace("[", "\\[").replace("]", "\\]")


def toc(md_string):
    """Takes a Markdown string, returns TOC string (in Markdown).

    Formats indented headers in []() style.
    """

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
    """Generator of (level: int, header: str) tuples from Markdown string."""
    is_comment_block = False
    for line in md_string.split("\n"):
        if line.startswith("```"):
            is_comment_block = not is_comment_block
        if is_comment_block:
            continue
        header = HEADER_PAT.match(line)
        if header:
            level = len(header.group(1))
            header = header.group(2).strip()
            yield level, header


def modify_and_write(path):
    """Write a table of contents to the Markdown file at `path`.

    Overwrites the file in place.

    If no tags or improper tags (<!---toc start--> and <!---toc end-->),
    raise MarkdownError before writing back.
    """

    with open(path) as fp:
        markdown = fp.read()
        table_of_contents = toc(markdown)

    new_markdown, replacements = TOC_PAT.subn(
        "<!---toc start-->\n\n{}\n\n<!---toc end-->".format(table_of_contents),
        markdown,
    )

    # If we couldn't find tags and 0 replacements were made, let user
    # know and raise.
    if not replacements:
        raise MarkdownError(
            "Document missing toc start/end tags.\n"
            "Add these delimiters to your Markdown file:\n\n"
            "\t<!---toc start-->\n"
            "\t<!---toc end-->\n\n"
            "Then, run:\n\n"
            "\t$ mdtoc %s" % path
        )

    elif replacements > 1:
        raise MarkdownError(
            "Multiple toc start/end tag pairs detected."
            " Your Markdown file should include only one pair of tags"
        )

    with open(path, "w") as fp:
        fp.write(new_markdown)
    print(colorize("Success: wrote TOC to {path}".format(path=path), ansi=22))


def get_links(md_string):
    """Find links in a Markdown string.

    Yields a 4-tuple:
    """
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

    for m in MD_LINK_PAT.finditer(md_string):
        line, col = line_col(m.start(1))
        yield m.group(1), m.group(2), line, col


_description = """
Generates table of contents for Markdown files.

The algorithm searches for the text blocks
between the delimiters:

<!---toc start--->
... anything ...
<!---toc end--->

The contents of the block are then replaced
by a table of contents.
"""


def parse_args():
    """Parse command-line arguments."""
    from mdtoc import __version__
    parser = argparse.ArgumentParser(
        description=_description,
        epilog="Created by Scott Frazer (https://github.com/scottfrazer).\n",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=__version__,
    )
    parser.add_argument(
        "--check-links",
        action="store_true",
        help="Find all hyperlinks and ensure that\nthey point to something valid",  # noqa
    )
    parser.add_argument(
        "markdown_file",
        help="Relative or abs. path of the Markdown\n(.md) file to overwrite",
    )
    return parser


def cli():
    """Command-line entry point."""
    parser = parse_args()
    cli = parser.parse_args()
    cli.markdown_file = os.path.expanduser(cli.markdown_file)

    try:
        modify_and_write(cli.markdown_file)
    except OSError:
        print(
            colorize(
                "Failed: "
                "Not found: {path}".format(path=cli.markdown_file),
                ansi=1
            )
        )
        return 1
    except MarkdownError as e:
        print(colorize("Failed: " + str(e), ansi=1))
        return 1

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
