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
