# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import os
import tempfile
import textwrap

import pytest

import mdtoc.main


@pytest.mark.parametrize(
    "header,out",
    [
        ("# This is an L1 header", "this-is-an-l1-header"),
        ("#   Spaces     here ...     ", "spaces-here-"),
        ("# THis is CAPS!!!", "this-is-caps"),
        ("## this is an l2 header", "this-is-an-l2-header"),
        ("### This is ... an L3 header??", "this-is--an-l3-header"),
        (
            "#### This is a Spicy Jalapeño Header! :)",
            "this-is-a-spicy-jalapeño-header-",
        ),
        (
            "# Чемезов заявил об уничтожении поврежденных штормом ракет С-400 для Китая",  # noqa
            "чемезов-заявил-об-уничтожении-поврежденных-штормом-ракет-с-400-для-китая",  # noqa
        ),
        ("### This has (some parens) in it", "this-has-some-parens-in-it"),
    ],
)
def test_as_link(header, out):
    assert mdtoc.main.as_link(header.lstrip("#").strip()) == out


def test_header_pat():
    headers = textwrap.dedent(
        """\
    # Header 1 here
    ## Header 3 here ...
    ### Header 4 Here ##"""
    )
    for line in headers.split("\n"):
        assert mdtoc.main.HEADER_PAT.match(line)


@pytest.mark.parametrize(
    "i,out",
    [
        (
            "[link here](https://github.com/scottfrazer/mdtoc/)",
            ("link here", "https://github.com/scottfrazer/mdtoc/"),
        ),
        (
            "[multi parens??](https://google.com/co(mp)uting(iscool))",
            ("multi parens??", "https://google.com/co(mp)uting(iscool)"),
        ),
    ],
)
def test_md_link_pat(i, out):
    match = mdtoc.main.MD_LINK_PAT.search(i)
    assert match
    assert match.group(1) == out[0]
    assert match.group(2) == out[1]


# ------------------
# Input/output pairs
# ------------------

_bad_markdown = (
    """\
# Welcome To Hell

<!---toc start-->
xxx
<!---toc end-->

## Okay so far

      ## Wait, This is Not a Header!!!

## Err ... ##

### Header 3

xxx""",
    """\
# Welcome To Hell

<!---toc start-->

* [Welcome To Hell](#welcome-to-hell)
  * [Okay so far](#okay-so-far)
  * [Err ... ##](#err--)
    * [Header 3](#header-3)

<!---toc end-->

## Okay so far

      ## Wait, This is Not a Header!!!

## Err ... ##

### Header 3

xxx""",
)

_good_markdown = (
    """\
# Welcome to Heaven

<!---toc start-->
<!---toc end-->
xxx

## Wow, Isn't This Neat!

xyz

```python

# Hopefully no one ever sees this
def f():
    return f(f()) - f()
```

All done.""",
    """\
# Welcome to Heaven

<!---toc start-->

* [Welcome to Heaven](#welcome-to-heaven)
  * [Wow, Isn't This Neat!](#wow-isnt-this-neat)

<!---toc end-->
xxx

## Wow, Isn't This Neat!

xyz

```python

# Hopefully no one ever sees this
def f():
    return f(f()) - f()
```

All done.""",
)

_missing_delims = (
    """\
x""",
    """\
x""",
)


def _mimic_cli(s):
    """Mimic reading & over-writing temporary files as done via CLI."""
    assert len(s) == 2, "Improper test tuple"
    i, out = s
    tmp = tempfile.NamedTemporaryFile(delete=False, mode="w")
    name = tmp.name
    tmp.write(i)
    tmp.close()
    # tmp.name is absolute path
    try:
        mdtoc.main.modify_and_write(name)
        tmp.close()
        with open(name) as f:
            assert f.read() == out
    finally:
        tmp.close()
        if os.path.isfile(name):
            os.remove(name)


@pytest.mark.parametrize("s", [_good_markdown, _bad_markdown])
def test_modify_and_write(s):
    _mimic_cli(s)


def test_modify_and_write_raises_no_delim():
    with pytest.raises(Exception):
        _mimic_cli(_missing_delims)
