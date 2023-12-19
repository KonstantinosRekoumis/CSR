from string import Template
from typing import Iterable

from modules.utils.resource import Resource


class LatexTemplate(Template):
    delimiter = "^^^"


class LatexFactory:

    def __init__(self):
        raise RuntimeError("Cannot instantiate static factory!")

    @staticmethod
    def get_latex_template(*path: str) -> LatexTemplate:
        """
        :param path: path of the latex template file; omit the toplevel "latex" "templates" directory
        """
        with Resource("templates", "latex", *path) as tex:
            return LatexTemplate(tex.handle.read())

    @staticmethod
    def substitute_template_values[T: Template](template: T, values: Iterable, separator: str = "\n") -> str:
        return separator.join([template.substitute(v) for v in values])
