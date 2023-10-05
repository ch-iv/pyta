from ast import literal_eval

from astroid import nodes
from pylint.checkers import BaseChecker
from pylint.checkers.utils import only_required_for_messages
from pylint.lint import PyLinter


class InvalidRangeIndexChecker(BaseChecker):
    name = "invalid_range_index"
    msgs = {
        "E9993": (
            "You should not use invalid range index on line %s",
            "invalid-range-index",
            "Used when you use invalid index range",
        )
    }
    # this is important so that your checker is executed before others
    priority = -1

    @only_required_for_messages("invalid-range-index")
    def visit_call(self, node: nodes.Call) -> None:
        if isinstance(node.func, nodes.Name):
            name = node.func.name
            # ignore the name if it's not a builtin (i.e. not defined in the
            # locals nor globals scope)
            if not (name in node.frame() or name in node.root()) and name == "range":
                args = node.args  # the arguments of 'range' call
                # guard nodes (e.g. Name) not properly handled by literal_eval.
                if any([not isinstance(arg, (nodes.Const, nodes.UnaryOp)) for arg in args]):
                    return

                eval_params = list(map(lambda z: literal_eval(z.as_string()), args))

                if (
                    len(args) == 0
                    or len(args) > 3
                    or not all([isinstance(c, int) for c in eval_params])
                ):
                    self.add_message("invalid-range-index", node=node, args=str(node.lineno))
                    return

                # set positional and default arguments of range
                arg0 = eval_params[0] if len(args) > 1 else 0
                arg2 = eval_params[2] if len(args) == 3 else 1
                arg1 = eval_params[0] if len(args) == 1 else eval_params[1]

                if not is_valid_range(arg0, arg1, arg2):
                    self.add_message("invalid-range-index", node=node, args=str(node.lineno))


def is_valid_range(arg0: int, arg1: int, arg2: int) -> bool:
    """Returns True if a range call with three arguments is valid.
    We consider a range to be valid if it has more than one element."""
    return (arg1 - arg0) / arg2 > 1


def register(linter: PyLinter) -> None:
    """required method to auto register this checker"""
    linter.register_checker(InvalidRangeIndexChecker(linter))
