from snake import *

def comment_lines(sel):
    lines = sel.split("\n")
    new_lines = []
    for line in lines:
        # only comment lines with content
        if line.strip():
            line = "# " + line
        new_lines.append(line)
    return "\n".join(new_lines)

def uncomment_lines(sel):
    lines = sel.split("\n")
    new_lines = []
    for line in lines:
        if line.lstrip().startswith("# "):
            line = line[2:]
        new_lines.append(line)
    return "\n".join(new_lines)


def toggle_bool():
    table = {
        "0": "1",
        "1": "0",
        "True": "False",
        "False": "True",
    }
    word = get_word()
    if word in table:
        replace_word(table[word])

def in_chars(start, end=None):
    if end is None:
        end = start
    first_pos = search(start, backwards=True, curline=True, move=False)
    last_pos = search(end, curline=True, move=False)
    found = first_pos and last_pos
    return found, first_pos, last_pos


def in_quotes():
    """ determines if our position is reasonably within quotes """
    def fn(quote_char):
        found, first_pos, last_pos = in_chars(quote_char)
        return found, first_pos, last_pos

    char = '"'
    found, first_pos, last_pos = fn(char)
    if not found:
        char = "'"
        found, first_pos, last_pos = fn(char)

    return found, first_pos, last_pos, char


def toggle_object_dict():
    found, first_pos, last_pos, quote_char = in_quotes()

    # if we're a dict
    if found:
        set_cursor_position(last_pos)
        keys("2x")
        set_cursor_position(first_pos)
        keys("hr.lx")

    # we're dotted notation
    else:
        word = delete_word()
        keys('Xi["' + word + '"]')


def toggle_quotes():
    table = {
        "'": '"',
        '"': "'",
    }

    found, first_pos, last_pos, quote_char = in_quotes()

    if found:
        opposite = table[quote_char]
        with preserve_cursor():
            set_cursor_position(first_pos)
            keys("r" + opposite)
            set_cursor_position(last_pos)
            keys("r" + opposite)
