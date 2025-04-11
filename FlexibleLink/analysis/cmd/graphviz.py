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
                index=['ω', 'G', 'SysPhase']
            )

    def __str__(self):
        return str(self.__dataframe)
    
    def ω(self) -> list[float]:
        return list(map(float, self.__dataframe.loc['ω'].to_list()))
    
    def G(self) -> list[float]:
        return list(map(float, self.__dataframe.loc['G'].to_list()))


def main():
    a = Args()
    data = AnalysisTarget(a.filename)

    print(data)
    print('ω =', data.ω(), type(data.ω()))

    figure = pyplot.figure()
    pyplot.title('Bode Gain plot')
    pyplot.xlabel('ω')
    pyplot.ylabel('20log|G(jω)|')
    pyplot.scatter(
        data.ω(),
        list(map(lambda x: 20 * math.log10(x), data.G())),
    )
    save_file_path = path.join(
        path.dirname(__file__),
        '..',
        'graph',
        f'{path.splitext(path.basename(a.filename))[0]}.graph.svg'
    )
    with open(save_file_path, mode='w') as f:
        figure.savefig(
            f,
            format='svg',
        )


if __name__ == "__main__":
    main()
