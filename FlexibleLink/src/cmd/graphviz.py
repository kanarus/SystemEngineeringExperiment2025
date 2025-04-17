from lib import plot, preprocess, fit
from lib.data import SampleData

import argparse
from os import path, makedirs

import numpy
from scipy import optimize
from matplotlib import pyplot


class Args:
    filename: str
    preopt: None | tuple[float, float, float, float, float]

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

        args = parser.parse_args()

        self.filename = args.filename
        self.preopt = args.preopt


def process_bode_gain_plot(p: plot.Plot) -> None:
    preprocess.filter_by_y_increase_continuity(p)
    preprocess.filter_by_vec_angle_continuity(p)
    preprocess.filter_by_y_increase_continuity(p, repeat_until_exaustaed=True)
    preprocess.amplify_valleys(p)


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
        d.SimplePlot().into_figure().savefig(f, format='svg')
    with open(path.join(save_dir, 'BodeGainPlot.svg'), mode='w') as f:
        d.BodeGainPlot().into_figure().savefig(f, format='svg')
    with open(path.join(save_dir, 'NyquistPlot.svg'), mode='w') as f:
        d.NyquistPlot().into_figure().savefig(f, format='svg')

    print('saved direct plots')

    with open(path.join(save_dir, 'BodeGainPlot.processed.svg'), mode='w') as f:
        p = d.BodeGainPlot()
        p.title = 'Bode Gain Plot (processed)'
        
        process_bode_gain_plot(p)

        if a.preopt is not None:
            preopt = tuple(a.preopt)
            print(f"preopt: {preopt}")
            pyplot.plot(
                p.x(),
                [fit.BodeGainCurve(x, *preopt) for x in p.x()],
                label='myopt',
                linestyle='--',
                color='green',
            )
        opt, cov = optimize.curve_fit(
            # lambda x, a3, a2, a1, b2, b0: fit.BodeGainCurve(10**x, a3, a2, a1, b2, b0),
            # xdata=[math.log10(x) for x in p.x()],
            # lambda x, a3, a2, a1, b2, b0: fit.BodeGainCurve(x, a3, a2, a1, b2, b0),
            fit.BodeGainCurve,
            xdata=p.x(),
            ydata=p.y(),
            # p0=[-9.44103211e+01, 2.68362545e+03, -2.53859031e+05, 1.18508982e+02, 3.10061565e+05]
            # p0=[0, 690, 1.6, -0.9, -320] if a.preopt is None else a.preopt,
            # p0 = [6.20118407e+01, 2.20686774e+03, 3.35098620e+04, -1.01441482e+02, -7.14178968e+04]
            # p0 = [6.20118407e+01, 2.20686774e+03, 3.35098620e+04, 1.01441482e+02, 7.14178968e+04]
            p0 = [6.78323768e+01, 2.25315109e+03, 4.65914534e+04, 1.01368177e+02, 7.13662697e+04]
        )
        print(f"optimal parameters: {opt}")
        print(f"standard deviation errors: {numpy.sqrt(numpy.diag(cov))}")
        
        fig = p.into_figure()
        pyplot.plot(
            p.x(),
            [fit.BodeGainCurve(x, *opt) for x in p.x()],
            label='fit',
            linestyle='--',
            color='red',
        )
        fig.savefig(f, format='svg')

    print('saved processed plots')


if __name__ == '__main__':
    main()
