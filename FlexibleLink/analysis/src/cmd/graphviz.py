from lib import preprocess, fit
from lib.data import SampleData

import math
import argparse
from os import path, makedirs

from scipy import optimize
from matplotlib import pyplot


class Args:
    filename: str

    def __init__(self):
        parser = argparse.ArgumentParser(description='take the target file name')
        parser.add_argument('filename', type=str, help='the target file name')
        args = parser.parse_args()

        self.filename = args.filename


def main():
    a = Args()
    d = SampleData(a.filename)

    print(d)

    save_dir = path.join(
        path.dirname(__file__),
        '..',
        '..',
        'plots',
        path.splitext(path.basename(a.filename))[0],
    )
    if not path.exists(save_dir):
        makedirs(save_dir)
    
    with open(path.join(save_dir, 'SimplePlot.svg'), mode='w') as f:
        d.SimplePlot().figure().savefig(f, format='svg')
    with open(path.join(save_dir, 'BodeGainPlot.svg'), mode='w') as f:
        d.BodeGainPlot().figure().savefig(f, format='svg')
    with open(path.join(save_dir, 'NyquistPlot.svg'), mode='w') as f:
        d.NyquistPlot().figure().savefig(f, format='svg')

    print('saved direct plots')

    with open(path.join(save_dir, 'BodeGainPlot.processed1.svg'), mode='w') as f:
        p = d.BodeGainPlot()
        p.title = 'Bode Gain Plot (processed by vec angle continuity)'
        preprocess.by_vec_angle_continuity(p)

        fig = p.figure()

        popt, _ = optimize.curve_fit(
            lambda x, a3, a2, a1, b2, b0: fit.BodeGainCurve(10**x, a3, a2, a1, b2, b0),
            xdata=[math.log10(x) for x in p.x()],
            ydata=p.y(),
            # p0=(
            #     1000,  # a3
            #     100,  # a2
            #     1,  # a1
            #     1,  # b2
            #     400,  # b0
            # ),
        )
        print(f"popt: {popt}")
        pyplot.plot(
            p.x(),
            [fit.BodeGainCurve(x, *popt) for x in p.x()],
            label='fit',
            linestyle='--',
            color='red',
        )

        fig.savefig(f, format='svg')

    with open(path.join(save_dir, 'BodeGainPlot.processed2.svg'), mode='w') as f:
        p = d.BodeGainPlot()
        p.title = 'Bode Gain Plot (processed by vec continuous connectivity score)'
        preprocess.by_vec_continuous_connectivity_score(p)

        fig = p.figure()

        popt, _ = optimize.curve_fit(
            lambda x, a3, a2, a1, b2, b0: fit.BodeGainCurve(10**x, a3, a2, a1, b2, b0),
            xdata=[math.log10(x) for x in p.x()],
            ydata=p.y(),
            # p0=(
            #     1.0,  # a3
            #     1.0,  # a2
            #     1.0,  # a1
            #     1.0,  # b2
            #     1.0,  # b0
            # ),
        )
        print(f"popt: {popt}")
        pyplot.plot(
            p.x(),
            [fit.BodeGainCurve(x, *popt) for x in p.x()],
            label='fit',
            linestyle='--',
            color='red',
        )

        fig.savefig(f, format='svg')
    
    print('saved processed plots')


if __name__ == '__main__':
    main()
