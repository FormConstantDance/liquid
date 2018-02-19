from snake import *
from . import helpers


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


def try_except(sel):
    first_line = sel.split("\n")[0]
    count = 0
    for char in first_line:
        if char == " ":
            count += 1
        else:
            break

    one_indent_num = 4
    space = " "
    one_indent = space * one_indent_num

    existing_spaces = space * count
    repl = existing_spaces + "try:\n"
    sel = helpers.indent(sel.rstrip("\n"), one_indent_num) + "\n"
    repl += sel
    repl += existing_spaces + "except Exception as e:\n"
    repl += existing_spaces + one_indent + "import pdb; pdb.set_trace()\n"
    return repl


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
