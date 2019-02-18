# Markdown TOC Generator

`mdtoc` is a command-line utility to generate table of contents within [Markdown](https://daringfireball.net/projects/markdown/) (.md) files.

<table>
  <tr>
    <td>Supports</td>
    <td>Python 2.7 | 3.4 | 3.5 | 3.6 | 3.7</td>
  </tr>
  <tr>
    <td>Latest Release</td>
    <td>
      <a href="https://pypi.org/project/mdtoc/">
      <img src="https://img.shields.io/pypi/v/mdtoc.svg" alt="latest release" />
      </a>
    </td>
  </tr>
  <tr>
    <td>Package Status</td>
    <td>
      <a href="https://pypi.org/project/mdtoc/">
      <img src="https://img.shields.io/pypi/status/mdtoc.svg" alt="status" /></td>
      </a>
  </tr>
  <tr>
    <td>License</td>
    <td>
      <a href="https://github.com/scottfrazer/mdtoc/blob/master/LICENSE">
      <img src="https://img.shields.io/pypi/l/mdtoc.svg" alt="license" />
      </a>
    </td>
  </tr>
</table>

## Install

Install via `pip install mdtoc`.

## Basic Usage

Add these delimiters to your Markdown file:

```
<!---toc start-->
<!---toc end-->
```

Then, from the command line, run:

```bash
$ mdtoc /path/to/myfile.md  # Overwrites in-place
```

This will overwrite the target file `your_markdown.md` in-place with the table of contents replacing the text _in between_ the delimiters marked above.  (The delimiters themselves are invisible comments when rendered.)

## Technical Details

`mdtoc` parses Markdown "atx-style" headers only: 1-6 hash characters (`#`) at the start of the line followed by the header.  It does *not* currently detect "setext-style" (underlined) headers.

The [Daring Fireball page](https://daringfireball.net/projects/markdown/syntax#header) is the closest thing that exists to an original, canonical syntax specification for Markdown.  (The page is created and hosted by John Gruber, the initial developer of Markdown as a language.)  However, this page leaves a good amount of ambiguity.  Because of that, **`mdtoc` also incorporates rules from [GitHub-flavored Markdown](https://github.github.com/gfm/#atx-heading)**, which gives a fuller specification:

> An ATX heading consists of a string of characters, parsed as inline content, between an opening sequence of 1–6 unescaped # characters and an optional closing sequence of any number of unescaped `#` characters. The opening sequence of `#` characters must be followed by a space or by the end of line. The optional closing sequence of `#`s must be preceded by a space and may be followed by spaces only. The opening # character may be indented 0-3 spaces. The raw contents of the heading are stripped of leading and trailing spaces before being parsed as inline content. The heading level is equal to the number of # characters in the opening sequence.

**Please consider the [GitHub-flavored Markdown](https://github.github.com/gfm/#atx-heading) rules to be the definitive empirical rulebook used by this tool.**  If you find a violation of that, pull requests are appreciated.

You can also check live examples in `tests/examples.md`.  This doc serves as touch-and-feel proof of GitHub's take on Markdown formatting, as well including some novel examples that even GitHub's page itself does not cover.

One break from GitHub is that this tool counts tabs as spaces, for all intents and purposes.  This is different from the GitHub specification, which defines a space strictly as `U+0020`.

Two other small notes:

- `mdtoc` will ignore comments prefaced with `#` that occur in Markdown code blocks (<code>\`\`\`</code>).
- `mdtoc` does *not* check for congruency/continuity of header levels.  If a level-3 header comes directly after a level-1 header, that is on you and will be rendered as-is.
