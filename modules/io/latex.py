import modules.render as rnr
from modules.io.datalogger import DataLogger
from modules.utils.logger import Logger


TEX_PREAMBLE = (
    '\\documentclass[12pt,a4paper]{report}\n'
    '\\usepackage[a4paper,headheight =15pt]{geometry}\n'
    '\\usepackage{array}\n'
    '\\usepackage{multirow}\n'
    '\\usepackage{longtable}\n'
    '\\usepackage{pdflscape}\n'
    '\\usepackage{amsmath}\n'
    '\\usepackage{comment}\n'
    '\\usepackage{caption}\n'
    '\\usepackage{graphicx}\n'
    '\\usepackage{fancyhdr}\n'
    '\\usepackage{typearea}\n'
    '\\usepackage[absolute]{textpos}\n'
    '\\fancypagestyle{normal}{\\fancyhf{}\\rhead{\\thepage}\\lhead{\\leftmark}\\setlength{\\headheight}{15pt}\n'
    '\\renewcommand{\\headrulewidth}{1pt} \n'
    '\\renewcommand{\\footrulewidth}{0pt}}\n'
    '\\fancypagestyle{lscape}{% \n'
    '\\fancyhf{} % clear all header and footer fields \n'
    '\\fancyhead[L]{%\n'
    '\\begin{textblock}{0}(1,12){\\rotatebox{90}{\\underline{\\leftmark}}}\\end{textblock}\n'
    '\\begin{textblock}{2}(1,1){\\rotatebox{90}{\\underline{\\thepage}}}\\end{textblock}}\n'
    '\\setlength{\\headheight}{15pt}\n'
    '\\setlength{\\footheight}{0pt}\n'
    '\\renewcommand{\\headrulewidth}{0pt} \n'
    '\\renewcommand{\\footrulewidth}{0pt}}\n'
    '\\graphicspath{{./}}\n'
)


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
    GeneralPart = (
    '\\chapter{General Input Data Particulars}\n'
    '\\label{sec:General Particulars}\n'
    '\\begin{table}[h]\n'
    '\\caption{Ship\'s General Input Data Particulars}\n'
    '\\label{tab:Gen_Part}\n'
    '\\begin{tabular}{{>{\centering}m{6cm}}*{2}{>{\centering}m{4cm}}}\n'
    '\\hline\n'
    '$L_{BP}$ '+f'&{ship.LBP}&'+' [m]\\tabularnewline \\hline\n'
    '$L_{sc} = L$ '+f'&{ship.Lsc}&'+' [m]\\tabularnewline \\hline\n'
    '$B$ '+f'&{ship.B}&'+' [m]\\tabularnewline \\hline\n'
    '$T$ '+f'&{ship.T}&'+' [m]\\tabularnewline \\hline\n'
    '$T_{min}$ '+f'&{ship.Tmin}&'+' [m]\\tabularnewline \\hline\n'
    '$T_{sc}$ '+f'&{ship.Tsc}&'+' [m]\\tabularnewline \\hline\n'
    '$D$ '+f'&{ship.D}&'+' [m]\\tabularnewline \\hline\n'
    '$C_b$ '+f'&{ship.Cb}&'+' \\tabularnewline \\hline\n'
    '$C_p$ '+f'&{ship.Cp}&'+' \\tabularnewline \\hline\n'
    '$C_m$ '+f'&{ship.Cm}&'+' \\tabularnewline \\hline\n'
    '$DWT$ '+f'&{ship.DWT}&'+' \\tabularnewline \\hline\n'
    'k (material factor) '+f'&{ship.kappa : 0.3g}&'+' [m]\\tabularnewline \\hline\n'
    '$M_{wh}$ '+f'&{round(ship.Mwh,2)}&'+' [kNm]\\tabularnewline \\hline\n'
    '$M_{ws}$ '+f'&{round(ship.Mws,2)}&'+' [kNm]\\tabularnewline \\hline\n'
    '$M_{sw,h-mid}$ '+f'&{round(ship.Msw_h_mid,2)}&'+' [kNm]\\tabularnewline \\hline\n'
    '$M_{sw,s-mid}$ '+f'&{round(ship.Msw_s_mid,2)}&'+' [kNm]\\tabularnewline \\hline\n'
    '$C_w$ '+f'&{round(ship.Cw,3)}&'+' \\tabularnewline \\hline\n'
    '$y_{neutral}$ '+f'&{round(ship.yo,3)}&'+' [m]\\tabularnewline \\hline\n'
    '$I_{net,\, v}$ '+f'&{round(ship.Ixx,2)}&'+' [$m^4$]\\tabularnewline \\hline\n'
    '$I_{n-50,\, v}$ '+f'&{round(ship.n50_Ixx,2)}&'+' [$m^4$]\\tabularnewline \\hline\n'
    '$a_0$   '+f'&{round(ship.a0,5)}&'+' \\tabularnewline \\hline\n'
    '\\end{tabular}\n'
    '\\end{table}\n\n')
    figures = ''
    if len(figs) != 0:
        for i in figs:
            figures +=(
                '\\begin{figure}[h]\n'
                '\\centering\n'
                '\\includegraphics[width=\linewidth]{'
                f'{i}'
                '}\n\\end{figure}\n'
            )
    pressure = (
        '\\newgeometry{margin=1.5cm}\n'
        '\\chapter{Pressure Data}\n'
        '\\label{sec:Pressure_Data}\n'
        + data_logger.get_tabular_pressure_data()
    )
    plates = (
        '\\chapter{Plating Data}\n'
        '\\label{sec:Plating_Data}\n'
        '\\newpage\n'
        '\\thispagestyle{lscape}\n'
        '\\pagestyle{lscape}\n'
        '\\begin{landscape}\n'
        + data_logger.get_tabular_plating_data() +
        '\\end{landscape}\n'
        '\\thispagestyle{normal}\n'
        '\\pagestyle{normal}\n'
    )
    stiffeners = (
        '\\chapter{Stiffeners Data}\n'
        '\\label{sec:Stiffeners_Data}\n'
        '\\newpage\n'
        '\\thispagestyle{lscape}\n'
        '\\pagestyle{lscape}\n'
        '\\begin{landscape}\n'
        + data_logger.get_tabular_stiffeners_data() +
        '\\end{landscape}\n'
        '\\thispagestyle{normal}\n'
        '\\pagestyle{normal}\n'
    )
    stiff_plates = (
        '\\clearpage'
        '\\chapter{Stiffened Plates Data}\n'
        '\\label{sec:Stiffened_Plates_Data}\n'
        + data_logger.get_tabular_stiffened_plates_data()
    )

    disclaimer = ""
    if ship.symmetrical:
        disclaimer = (
            "Due to the vessel having a symmetrical cross section, "
            "Area and Area Inertia Moments are double the stiffened plates sums.\n"
        )

    ordinary_section = (
        '\\chapter{Ordinary Section\'s Stiffened Plates Data}\n'
        '\\label{sec:Stiffeners Data}\n'
        + disclaimer + data_logger.get_tabular_ordinary_stiffeners_data()
    )

    mid += GeneralPart + figures + pressure + plates + stiffeners + stiff_plates + ordinary_section + '\\clearpage\\restoregeometry'

    if standalone:
        out = TEX_PREAMBLE + '\\begin{document}' + mid + '\\end{document}'
    else:
        out = mid

    Logger.debug(out)

    Logger.debug(out)

    return out
