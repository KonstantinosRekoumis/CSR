from typing import Iterable

import modules.render as rnr
from modules.io.datalogger import DataLogger
from modules.io.templates import TemplateFactory
from modules.utils.logger import Logger

preamble_template = TemplateFactory.get_latex_template("report", "preamble.tex")
particulars_data_template = TemplateFactory.get_latex_template("chapters", "particulars.tex")
figure_template = TemplateFactory.get_latex_template("report", "figure.tex")
pressure_data_template = TemplateFactory.get_latex_template("chapters", "pressure_data.tex")
plating_data_template = TemplateFactory.get_latex_template("chapters", "plating_data.tex")
stiffeners_data_template = TemplateFactory.get_latex_template("chapters", "stiffeners_data.tex")
stiffened_data_template = TemplateFactory.get_latex_template("chapters", "stiffened_data.tex")
stiffened_ordinary_data_template = TemplateFactory.get_latex_template("chapters", "stiffened_ordinary_data.tex")
content_template = TemplateFactory.get_latex_template("report", "content.tex")
Logger.debug("Done loading latex.py templates.")


def generate_latex_rep(data: DataLogger, path='./', standalone=True):
    out = latex_output(data, embeddable=not standalone, figs=('id_plt.pdf', 'tag_plt.pdf', 'PSM_plt.pdf'))
    with open(path + 'tabs.tex', 'w') as file:
        file.write(out)
    rnr.contour_plot(data.ship, key="id", path=path + 'id_plt.pdf', cmap='jet')
    rnr.contour_plot(data.ship, key="spacing", path=path + 'PSM_plt.pdf', cmap='jet')
    rnr.contour_plot(data.ship, key="tag", path=path + 'tag_plt.pdf', cmap='jet')


def latex_output(data_logger: DataLogger, embeddable=True, figs: Iterable = ()) -> str:
    """
    Generates a latex document.
    :param embeddable: If True, returns an embeddable LaTeX string.
    :param figs: Iterable of figures to embed in the document.
    """
    data_logger.create_tabular_data()
    disclaimer = ""
    if data_logger.ship.symmetrical:
        disclaimer = (
            "Due to the vessel having a symmetrical cross section, "
            "Area and Area Inertia Moments are double the stiffened plates sums."
        )

    particulars = particulars_data_template.substitute(data_logger.ship.map_members())
    figures = TemplateFactory.substitute_template_values(figure_template, list(map(lambda o: str(o), figs)))
    pressure = pressure_data_template.substitute(data=data_logger.get_tabular_pressure_data())
    plates = plating_data_template.substitute(data=data_logger.get_tabular_plating_data())
    stiffeners = stiffeners_data_template.substitute(data=data_logger.get_tabular_stiffeners_data())
    stiffened_plates = stiffened_data_template.substitute(data=data_logger.get_tabular_stiffened_plates_data())
    ordinary_section = stiffened_ordinary_data_template.substitute(
        disclaimer=disclaimer,
        data=data_logger.get_tabular_ordinary_stiffeners_data()
    )
    content = content_template.substitute(
        particulars=particulars,
        figures=figures,
        pressure=pressure,
        plates=plates,
        stiffeners=stiffeners,
        stiffened_plates=stiffened_plates,
        ordinary_section=ordinary_section
    )

    if embeddable:
        Logger.debug(content)
        return content

    out = preamble_template.substitute(content=content)
    Logger.debug(out)
    return out
