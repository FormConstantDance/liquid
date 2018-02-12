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

def toggle_quotes():
    table = {
        "'": '"',
        '"': "'",
    }

    def fn(quote_char):
        opposite = table[quote_char]

        def replace():
            keys("r" + opposite)

        first_pos = search(quote_char, backwards=True, curline=True, move=False)
        last_pos = search(quote_char, curline=True, move=False)
        found = first_pos and last_pos

        if found:
            with preserve_cursor():
                set_cursor_position(first_pos)
                replace()
                set_cursor_position(last_pos)
                replace()

        return found

    found = fn('"')
    if not found:
        fn("'")
