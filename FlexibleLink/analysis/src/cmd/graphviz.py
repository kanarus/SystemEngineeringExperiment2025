from lib.data import SampleData

import math
import argparse
from os import path, makedirs
from matplotlib import pyplot


class Args:
    filename: str

    def __init__(self):
        parser = argparse.ArgumentParser(description='take the target file name')
        parser.add_argument('filename', type=str, help='the target file name')
        args = parser.parse_args()

        self.filename = args.filename


class GraphViz:
    __data: SampleData

    def __init__(self, sample_data: SampleData):
        self.__data = sample_data

    def SimplePlot(self) -> pyplot.Figure:
        figure = pyplot.figure()
        pyplot.title('Simple Plot')
        pyplot.xlabel('ω [rad/sec]')
        pyplot.ylabel('G(jω)')
        pyplot.grid()
        pyplot.scatter(
            x=self.__data.ω,
            y=self.__data.SysGain,
            s=8,
        )
        return figure
    
    def BodeGainPlot(self) -> pyplot.Figure:
        plot = self.__data.BodeGainPlot()
        figure = pyplot.figure()
        pyplot.title('Bode Gain Plot')
        pyplot.xscale('log')
        pyplot.xlabel('ω [rad/sec]')
        pyplot.ylabel('20log|G(jω)|')
        pyplot.grid()
        pyplot.scatter(plot.x, plot.y, s=8)
        return figure

    def NyquistPlot(self) -> pyplot.Figure:
        plot = self.__data.NyquistPlot()
        figure = pyplot.figure()
        pyplot.title('Nyquist Plot')
        pyplot.xlabel('Re(G(jω))')
        pyplot.ylabel('Im(G(jω))')
        pyplot.grid()
        pyplot.scatter(plot.x, plot.y, s=8)
        return figure


def main():
    a = Args()
    data = SampleData(a.filename)

    print(data)

    gv = GraphViz(data)

    save_dir = path.join(
        path.dirname(__file__),
        '..',
        '..',
        'graph',
        path.splitext(path.basename(a.filename))[0],
    )
    if not path.exists(save_dir):
        makedirs(save_dir)
    
    with open(path.join(save_dir, 'SimplePlot.svg'), mode='w') as f:
        gv.SimplePlot().savefig(f, format='svg')
    with open(path.join(save_dir, 'BodeGainPlot.svg'), mode='w') as f:
        gv.BodeGainPlot().savefig(f, format='svg')
    with open(path.join(save_dir, 'NyquistPlot.svg'), mode='w') as f:
        gv.NyquistPlot().savefig(f, format='svg')

    print('saved plots')


if __name__ == "__main__":
    main()
