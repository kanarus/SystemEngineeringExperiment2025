from lib import preprocess, fit
from lib.data import SampleData

import math
import argparse
from os import path, makedirs

from scipy import optimize
from matplotlib import pyplot


class Args:
    filename: str
    preopt1: None | tuple[float, float, float, float, float]
    preopt2: None | tuple[float, float, float, float, float]

    def __init__(self):
        parser = argparse.ArgumentParser(description='take the target file name')
        parser.add_argument('filename', type=str, help='the target file name')
        parser.add_argument(
            '-p',
            '--preopt',
            type=float,
            nargs=5,
            help='the preopt parameters for BodeGainCurve',
        )
        parser.add_argument(
            '-p1',
            '--preopt1',
            type=float,
            nargs=5,
            help='the preopt parameters for BodeGainCurve processed 1',
        )
        parser.add_argument(
            '-p2',
            '--preopt2',
            type=float,
            nargs=5,
            help='the preopt parameters for BodeGainCurve processed 2',
        )
        args = parser.parse_args()

        self.filename = args.filename
        self.preopt1 = args.preopt1
        self.preopt2 = args.preopt2
        if args.preopt is not None:
            self.preopt1 = args.preopt
            self.preopt2 = args.preopt


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
        preprocess.amplify_valleys(p)

        if a.preopt1 is not None:
            preopt = tuple(a.preopt1)
            print(f"preopt: {preopt}")
            pyplot.plot(
                p.x(),
                [fit.BodeGainCurve(x, *preopt) for x in p.x()],
                label='myopt',
                linestyle='--',
                color='green',
            )
        popt, _ = optimize.curve_fit(
            # lambda x, a3, a2, a1, b2, b0: fit.BodeGainCurve(10**x, a3, a2, a1, b2, b0),
            # xdata=[math.log10(x) for x in p.x()],
            # lambda x, a3, a2, a1, b2, b0: fit.BodeGainCurve(x, a3, a2, a1, b2, b0),
            fit.BodeGainCurve,
            xdata=p.x(),
            ydata=p.y(),
            p0=[0, 690, 1.6, -0.9, -320] if a.preopt1 is None else a.preopt1,
            # p0 = [6.20118407e+01, 2.20686774e+03, 3.35098620e+04, -1.01441482e+02, -7.14178968e+04]
            # p0=[-9.44103211e+01, 2.68362545e+03, -2.53859031e+05, 1.18508982e+02, 3.10061565e+05]
        )
        print(f"popt: {popt}")

        fig = p.figure()
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
        preprocess.amplify_valleys(p)

        fig = p.figure()

        if a.preopt2 is not None:
            preopt = tuple(a.preopt2)
            print(f"preopt: {preopt}")
            pyplot.plot(
                p.x(),
                [fit.BodeGainCurve(x, *preopt) for x in p.x()],
                label='myopt',
                linestyle='--',
                color='green',
            )
        popt, _ = optimize.curve_fit(
            lambda x, a3, a2, a1, b2, b0: fit.BodeGainCurve(10**x, a3, a2, a1, b2, b0),
            xdata=[math.log10(x) for x in p.x()],
            ydata=p.y(),
            p0=[0, -24, -9.2, -2.2, -414] if a.preopt2 is None else a.preopt2,
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
