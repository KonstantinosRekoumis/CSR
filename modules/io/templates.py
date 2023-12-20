from string import Template
from typing import Iterable

from modules.utils.resource import Resource


class LatexTemplate(Template):
    delimiter = "^^^"


# noinspection PyCallingNonCallable
class TemplateFactory:

    def __init__(self):
        raise RuntimeError("Cannot instantiate static factory!")

    @staticmethod
    def get_template[T: type[Template]](*path: str, cls: T = Template) -> T:
        """
        :param path: path of the template file
        :param cls: subclass of string.Template to instantiate. Defaults to string.Template.
        """
        with Resource(*path) as tex:
            return cls(tex.handle.read())

    @staticmethod
    def get_latex_template(*path: str) -> LatexTemplate:
        """
        :param path: path of the latex template file; omit the toplevel "latex" "templates" directory
        """
        with Resource("templates", "latex", *path) as tex:
            return LatexTemplate(tex.handle.read())

    @staticmethod
    def substitute_template_values[T: Template](template: T, values: Iterable, separator: str = "\n") -> str:
        """
        :returns: A separator joined string of template T, substituted with values.
        """
        return separator.join([template.substitute(v) for v in values])
