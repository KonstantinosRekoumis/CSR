import modules.render as rnr
from modules.io.datalogger import DataLogger
from modules.io.templates import LatexFactory
from modules.utils.logger import Logger

# old preamble / out
preamble_template = LatexFactory.get_latex_template("report", "preamble.tex")
# old GeneralPart
particulars_data_template = LatexFactory.get_latex_template("chapters", "particulars.tex")
# old figures
figure_template = LatexFactory.get_latex_template("report", "figure.tex")
# FIXME LatexFactory.substitute_template_values(figure_template, figures)
# old pressure
pressure_data_template = LatexFactory.get_latex_template("chapters", "pressure_data.tex")
# old plates
plating_data_template = LatexFactory.get_latex_template("chapters", "plating_data.tex")
# old stiffeners
stiffeners_data_template = LatexFactory.get_latex_template("chapters", "stiffeners_data.tex")
# old stiff_plates
stiffened_data_template = LatexFactory.get_latex_template("chapters", "stiffened_data.tex")
# old ordinary_section
stiffened_ordinary_data_template = LatexFactory.get_latex_template("chapters", "stiffened_ordinary_data.tex")
# old mid
content_template = LatexFactory.get_latex_template("report", "content.tex")


def generate_latex_rep(data: DataLogger, path='./', _standalone=True):
    out = latex_output(data, standalone=_standalone, figs=('id_plt.pdf', 'tag_plt.pdf', 'PSM_plt.pdf'))
    with open(path + 'tabs.tex', 'w') as file:
        file.write(out)
    rnr.contour_plot(data.ship, key="id", path=path + 'id_plt.pdf', cmap='jet')
    rnr.contour_plot(data.ship, key="spacing", path=path + 'PSM_plt.pdf', cmap='jet')
    rnr.contour_plot(data.ship, key="tag", path=path + 'tag_plt.pdf', cmap='jet')


def latex_output(data_logger : DataLogger, standalone=False, figs=()):
    """
    Output Function that generates a .tex file for use in LaTeX
    """
    data_logger.create_tabular_data()
    ship = data_logger.ship
    mid = ''
    GeneralPart =  # FIXME
    figures = ''
    if len(figs) != 0:
        for i in figs:
            figures += # FIXME
    pressure = # FIXME
    plates = # FIXME
    stiffeners = # FIXME
    stiff_plates = # FIXME

    disclaimer = ""
    if ship.symmetrical:
        disclaimer = (
            "Due to the vessel having a symmetrical cross section, "
            "Area and Area Inertia Moments are double the stiffened plates sums.\n"
        )

    ordinary_section = # FIXME

    mid = # FIXME

    out = # FIXME
    if standalone:
        out = # FIXME with preamble

    Logger.debug(out)

    return out
