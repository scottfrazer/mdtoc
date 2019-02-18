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
$ mdtoc your_markdown.md
```

This will overwrite the target file `your_markdown.md` in-place with the table of contents replacing the text _in between_ the delimiters marked above.  (The delimiters themselves are invisible comments when rendered.)

## Technical Details

`mdtoc` parses [Markdown "atx-style" headers](https://daringfireball.net/projects/markdown/syntax#header) only: 1-6 hash characters (`#`) at the start of the line.  It does *not* currently detect "setext-style" (underlined) headers.

Some ground rules:

- No leading whitespace is allowed before the hash characters.
- Whitespace after initial hash(es) is optional and is not part of title.
- Closing hashes are optional and do not need to match opening hashes in number; they are not part of title.
- Trailing spaces in the title are not part of title.  (All surrounding whitespace is stripped.)
- `mdtoc` will ignore comments prefaced with `#` that occur in Markdown code blocks (<code>\`\`\`</code>).
- `mdtoc` does *not* check for congruency/continuity of header levels.  If a level-3 header comes directly after a level-1 header, that is on you and will be rendered as-is.

How did we build these rules?

The [Daring Fireball](https://daringfireball.net/projects/markdown/) page is the closest thing that exists to a canonical syntax specification for Markdown.  (The page is created and hosted by John Gruber, the original developer of Markdown as a language.)

Because this page leaves some ambiguity, we also use the Sublime Text [MarkdownPreview](https://github.com/facelessuser/MarkdownPreview) tool as a basis for formatting rules.  In development, this consists of inferring syntax rules from input/output testing of real .md headers rendered using MarkdownPreview.
