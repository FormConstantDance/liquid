from snake import *
import ast
import __builtin__


class NodeVisitorWithParent(ast.NodeVisitor):
    """ almost identical to ast.NodeVisitor, this only adds passing the parent
    node to the helper methods """
    def visit(self, node, parent):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, parent)

    def generic_visit(self, node, parent):
        parent = node
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        self.visit(item, parent)
            elif isinstance(value, ast.AST):
                self.visit(value, parent)

class GlobalNameAggregator(NodeVisitorWithParent):
    """ finds all global names, namely imports and assigns """
    def __init__(self):
        self.global_names = set()

    def visit_FunctionDef(self, node, parent):
        if isinstance(parent, ast.Module):
            self.global_names.add((node.name, node.lineno))
        self.generic_visit(node, parent)


    def visit_Assign(self, node, parent):
        if isinstance(parent, ast.Module):
            for assign in node.targets:
                name = assign.id
                self.global_names.add((name, node.lineno))
        self.generic_visit(node, parent)

    def visit_Import(self, node, parent):
        if isinstance(parent, ast.Module):
            for alias in node.names:
                mod_name = alias.asname or alias.name
                self.global_names.add((mod_name, node.lineno))
        self.generic_visit(node, parent)

class DefinedNamesAggregator(NodeVisitorWithParent):
    """ used to find all defined names between start_line and end_line """

    def __init__(self, start_line, end_line, predefined):
        self.start_line = start_line
        self.end_line = end_line
        self.defined_names = predefined.copy()
        self.used_names = set()

    def visit_Name(self, node, parent):
        node_lineno = getattr(node, "lineno", None)
        is_load = isinstance(node.ctx, ast.Load)
        if is_load and node_lineno >= self.start_line and node_lineno <= self.end_line:
            self.used_names.add(node.id)
        self.generic_visit(node, parent)

    def visit_Assign(self, node, parent):
        node_lineno = getattr(node, "lineno", None)

        if node_lineno >= self.start_line and node_lineno <= self.end_line:
            for assign in node.targets:
                if isinstance(assign, ast.Attribute):
                    continue
                name = assign.id
                self.defined_names.add(name)

        self.generic_visit(node, parent)



def get_globals_before(root, before_line):
    """ finds all global names defined before """
    visitor = GlobalNameAggregator()
    visitor.visit(root, None)

    defined_globals = set()
    for name, line in visitor.global_names:
        if line <= before_line:
            defined_globals.add(name)

    return defined_globals


def build_def_function(name, args, body, num_spaces=4):
    """ name is a function name, args is a list of arguments, body is a string
    body for the function, and num_spaces is the space preferences for tabbing.
    the return result is a string containing a new function """
    lines = []
    body = body.split("\n")

    # determine our spacing situation of the body
    first_line = body[0]
    leading_spaces = len(first_line) - len(first_line.lstrip())

    arg_str = ", ".join(args)
    lines.append("def %s(%s):" % (name, arg_str))
    for line in body:
        line = line[leading_spaces:]
        lines.append((" " * num_spaces) + line)
    return "\n".join(lines)


def build_call_function(name, args):
    arg_str = ", ".join(args)
    return "%s(%s)" % (name, arg_str)


def get_undefined_names(root, start, end):
    predefined = set(dir(__builtin__)) | get_globals_before(root, start)
    visitor = DefinedNamesAggregator(start, end, predefined)
    visitor.visit(root, None)
    undefined_names = visitor.used_names - visitor.defined_names
    return undefined_names

def refactor_code(sel, start, end, all_src):
    tree = ast.parse(all_src)
    fn_args = list(get_undefined_names(tree, start, end))
    fn_name = "fn"
    fn_str = build_def_function(fn_name, fn_args, sel.rstrip())
    fn_call = build_call_function(fn_name, fn_args)
    return fn_str, fn_call

def indent(block, amount):
    return "\n".join([(" " * amount) + line for line in block.split("\n")])

def refactor_into_function(sel):
    whole_file = get_current_buffer_contents()
    ((start_line, _), (end_line, _)) = get_visual_range()
    new_def, new_call = refactor_code(sel, start_line, end_line, whole_file)

    leading_spaces = len(sel) - len(sel.lstrip())
    new_def = indent(new_def, leading_spaces)
    new_call = indent(new_call, leading_spaces)

    return new_def + "\n" + new_call + "\n"
