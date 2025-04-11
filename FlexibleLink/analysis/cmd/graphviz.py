import csv
import argparse
import math
from os import path
from matplotlib import pyplot
from pandas import DataFrame


class Args:
    filename: str

    def __init__(self):
        parser = argparse.ArgumentParser(description='take the target file name')
        parser.add_argument('filename', type=str, help='the target file name')
        args = parser.parse_args()

        self.filename = args.filename


class AnalysisTarget:
    __dataframe: DataFrame

    def __init__(self, filename: str):
        with open(filename, mode='r') as f:
            self.__dataframe = DataFrame(
                list(csv.reader(f)),
                index=['ω', 'SysGain', 'SysPhase']
            )

    def __str__(self):
        return str(self.__dataframe)
    
    def ω(self) -> list[float]:
        return list(map(float, self.__dataframe.loc['ω'].to_list()))
    
    def SysGain(self) -> list[float]:
        return list(map(float, self.__dataframe.loc['SysGain'].to_list()))
    
    def SysPhase(self) -> list[float]:
        return list(map(float, self.__dataframe.loc['SysPhase'].to_list()))
    
    def saveBodeGainPlot(self, filename: str) -> None:
        figure = pyplot.figure()
        pyplot.title('Bode Gain Plot')
        pyplot.xscale('log')
        pyplot.xlabel('ω [rad/sec]')
        pyplot.ylabel('20log|G(jω)|')
        pyplot.grid()
        pyplot.scatter(
            x=self.ω(),
            y=list(map(lambda x: 20 * math.log10(x), self.SysGain())),
            s=8,
        )
        with open(filename, mode='w') as f:
            figure.savefig(f, format='svg')

    def saveNyquistPlot(self, filename: str) -> None:
        figure = pyplot.figure()
        pyplot.title('Nyquist Plot')
        pyplot.xlabel('Re(G(jω))')
        pyplot.ylabel('Im(G(jω))')
        pyplot.grid()
        pyplot.scatter(
            x=list(map(lambda x, y: x * math.cos(y), self.SysGain(), self.SysPhase())),
            y=list(map(lambda x, y: x * math.sin(y), self.SysGain(), self.SysPhase())),
            s=8,
        )
        with open(filename, mode='w') as f:
            figure.savefig(f, format='svg')


def main():
    a = Args()
    data = AnalysisTarget(a.filename)

    print(data)
    print('ω =', data.ω(), type(data.ω()))

    data.saveBodeGainPlot(path.join(
        path.dirname(__file__),
        '..',
        'graph',
        f'{path.splitext(path.basename(a.filename))[0]}.BodeGainPlot.svg'
    ))
    data.saveNyquistPlot(path.join(
        path.dirname(__file__),
        '..',
        'graph',
        f'{path.splitext(path.basename(a.filename))[0]}.NyquistPlot.svg'
    ))

if __name__ == "__main__":
    main()
