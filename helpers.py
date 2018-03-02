def indent(block, amount=4):
    return "\n".join([(" " * amount) + line for line in block.split("\n")])
