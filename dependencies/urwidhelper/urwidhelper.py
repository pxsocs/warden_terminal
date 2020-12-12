"""
The MIT License (MIT)
Copyright © 2020 Michael Franklin

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

==

Urwid Helper

    Primarily this script converts an ANSII escaped string for display on urwid.

    Methods:
        - translate_text_for_urwid: Converts an ANSII escaped string into an urwid equivalent.
        - translate_color: Convert a 3/4 bit ANSII escape code into the equivalent urwid color
        - get_ansii_group_matches_for_text: Get a iterator of (ansicodes: int[], text: str) found within the text.

    Derived from:
        https://github.com/Nanoseb/ncTelegram/blob/master/ncTelegram/ui_msgwidget.py#L218
"""

import re
import urwid
from typing import Tuple, List, Union, Iterator
"""
Explained using: https://regex101.com/

    [\x1b\033]          match one of "\x1b" or "\033"
    \[                  match "[" (literal)
    (                   capture group 1
        [\d;]+              integer or literal ';' literal (one or many)
    )                   end capture group 1
    m                   match "m" literal
    (                   capture group 2
        [^\x1b\033]+        match all characters but "\x1b" or "\033" (text between next group)
    )                   end capture group 2
"""
ANSI_ESCAPE_REGEX = r"[\x1b\033]\[([\d;]+)m([^\x1b\033]+)"

fg_lookup = {
    30: "black",
    31: "dark red",
    32: "dark green",
    33: "brown",
    34: "dark blue",
    35: "dark magenta",
    36: "dark cyan",
    37: "light gray",
    90: "dark gray",
    91: "light red",
    92: "light green",
    93: "yellow",
    94: "light blue",
    95: "light magenta",
    96: "light cyan",
    97: "white",
}

bg_lookup = {
    40: "black",
    41: "dark red",
    42: "dark green",
    43: "brown",
    44: "dark blue",
    45: "dark magenta",
    46: "dark cyan",
    47: "light gray",
    100: "dark gray",
    101: "light red",
    102: "light green",
    103: "yellow",
    104: "light blue",
    105: "light magenta",
    106: "light cyan",
    107: "white",
}


def translate_color(attr: Union[str, Tuple, List[int]]) -> Tuple[str, str]:
    """
    Translates a 3/4 bit ANSII escape code into the equivalent urwid color:
    Source: https://en.wikipedia.org/wiki/ANSI_escape_code#3/4_bit

    >>> translate_color([91])
    ('light red', '')

    >>> translate_color([91])
    ('light red', '')

    >>> translate_color([107])
    ('', 'white')

    >>> translate_color([91, 101])
    ('light red', 'light red')

    >>> translate_color("91;101")
    ('light red', 'light red')

    >>> translate_color("")
    ('', '')

    :param attr: string (should be semi-colon (;) delimited) | Tuple | List[int]
    :return: Tuple[foreground: str, background: str]

    """
    if isinstance(attr, int):
        list_attr = [attr]
    elif isinstance(attr, (tuple, list)):
        list_attr = attr
    elif isinstance(attr, str):
        list_attr = [int(i) for i in attr.split(";") if len(i) > 0]
    else:
        list_attr = [0]

    fg = ''
    bg = ''

    for elem in list_attr:
        if elem == 0:
            # reset, special case
            fg, bg = '', ''
            continue

        if elem in fg_lookup:
            fg = fg_lookup[elem]
        if elem in bg_lookup:
            bg = bg_lookup[elem]

    return fg, bg


def get_ansii_group_matches_for_text(text: str
                                     ) -> Iterator[Tuple[List[int], str]]:
    """
    Get a iterator of (ansicodes: int[], text: str) found from the text.

    >>> list(get_ansii_group_matches_for_text("\033[91mHello, world"))
    [([91], 'Hello, world')]

    >>> list(get_ansii_group_matches_for_text("\033[91mHello, world\033[97mHello, world"))
    [([91], 'Hello, world'), ([97], 'Hello, world')]

    >>> list(get_ansii_group_matches_for_text("\033[91mHello, world\\nHi"))
    [([91], 'Hello, world\\nHi')]
    """
    for match in re.finditer(ANSI_ESCAPE_REGEX, text, re.DOTALL):
        attr = match.group(1)
        parsed_attr = [int(i) for i in attr.split(";")]
        text = match.group(2)

        yield parsed_attr, text


def translate_text_for_urwid(raw_text):
    """
    Converts an ANSII escaped string into an urwid equivalent.
    First by finding all the matches for "\033[" or "\x1b[",
    reading the ANSII escape code(s) (semi-colon delimited),
    and converting these to the an urwid AttrSpec.

    >>> translate_text_for_urwid("\033[91mHello, world")
    [(AttrSpec('light red', 'default'), 'Hello, world')]

    >>> translate_text_for_urwid("\033[97;101mHello, world")
    [(AttrSpec('white', 'light red'), 'Hello, world')]

    >>> translate_text_for_urwid("\033[0mFin, reset everything")
    [(AttrSpec('default', 'default'), 'Fin, reset everything')]

    :param raw_text:
    :return:
    """

    formated_text = []
    if hasattr(raw_text, "decode"):
        raw_text = raw_text.decode("utf-8")

    # Reset the start of text (+ allow for text that isn't formatted)
    if not (raw_text.startswith("\033[") or raw_text.startswith("\x1b[")):
        raw_text = "\x1b[0m" + raw_text

    for (attr, text) in get_ansii_group_matches_for_text(raw_text):
        fgcolor, bgcolor = translate_color(attr)
        formated_text.append((urwid.AttrSpec(fgcolor, bgcolor), text))

    return formated_text


if __name__ == "__main__":
    import doctest
    doctest.testmod()