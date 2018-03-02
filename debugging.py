import re
import libtmux as tmux

def parse_file(line):
    m = re.search(r"File \"(.+?)\", line (\d+), in", line)
    filename = m.group(1)
    line = int(m.group(2))
    return filename, line


def find_tb(lines):
    m = "Traceback (most recent call last):"
    tb_found = False
    for idx, line in enumerate(reversed(lines)):
        if line == m:
            tb_found = len(lines) - idx - 1
            break

    stack = None

    if tb_found is not False:
        stack = []
        for line in lines[tb_found+1:]:
            if not line.startswith(" "):
                break

            m = re.match(r"\s{2}\b", line)
            if m:
                filename, line = parse_file(line)
                stack.append((filename, line))

    return stack


def find_traceback():
    server = tmux.Server()
    sess_name = server.cmd("display-message", "-p", "#S").stdout[0]
    sess = server.find_where({"session_name": sess_name})
    window = sess.attached_window

    stack = None
    found_pane = None
    for pane in window.panes:
        lines = get_contents(pane)
        stack = find_tb(lines)
        if stack:
            found_pane = pane
            break

    return found_pane, stack


def get_contents(pane):
    """ return the contents of a pane as a list of lines """
    lines = pane.cmd("capture-pane", "-p", "-J").stdout
    return lines


if __name__ == "__main__":
    print(find_traceback())
