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
    __sample_data: SampleData

    def __init__(self, sample_data: SampleData):
        self.__sample_data = sample_data

    def SimplePlot(self) -> pyplot.Figure:
        figure = pyplot.figure()
        pyplot.title('Simple Plot')
        pyplot.xlabel('ω [rad/sec]')
        pyplot.ylabel('G(jω)')
        pyplot.grid()
        pyplot.scatter(
            x=self.__sample_data.ω(),
            y=self.__sample_data.SysGain(),
            s=8,
        )
        return figure
    
    def BodeGainPlot(self) -> pyplot.Figure:
        figure = pyplot.figure()
        pyplot.title('Bode Gain Plot')
        pyplot.xscale('log')
        pyplot.xlabel('ω [rad/sec]')
        pyplot.ylabel('20log|G(jω)|')
        pyplot.grid()
        pyplot.scatter(
            x=self.__sample_data.ω(),
            y=list(map(lambda x: 20 * math.log10(x), self.__sample_data.SysGain())),
            s=8,
        )
        return figure

    def NyquistPlot(self) -> pyplot.Figure:
        figure = pyplot.figure()
        pyplot.title('Nyquist Plot')
        pyplot.xlabel('Re(G(jω))')
        pyplot.ylabel('Im(G(jω))')
        pyplot.grid()
        pyplot.scatter(
            x=list(map(lambda x, y: x * math.cos(y), self.__sample_data.SysGain(), self.__sample_data.SysPhase())),
            y=list(map(lambda x, y: x * math.sin(y), self.__sample_data.SysGain(), self.__sample_data.SysPhase())),
            s=8,
        )
        return figure


def main():
    a = Args()
    data = SampleData(a.filename)

    print(data)

    graph_viz = GraphViz(data)

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
        graph_viz.SimplePlot().savefig(f, format='svg')
    with open(path.join(save_dir, 'BodeGainPlot.svg'), mode='w') as f:
        graph_viz.BodeGainPlot().savefig(f, format='svg')
    with open(path.join(save_dir, 'NyquistPlot.svg'), mode='w') as f:
        graph_viz.NyquistPlot().savefig(f, format='svg')

    print('saved plots')


if __name__ == "__main__":
    main()
