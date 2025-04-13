from lib import preprocess
from lib.data import SampleData

import argparse
from os import path, makedirs


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
        'graph',
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
        preprocess.by_vec_angle_continuity(p)
        p.title = 'Bode Gain Plot (processed by vec angle continuity)'
        p.figure().savefig(f, format='svg')
    with open(path.join(save_dir, 'BodeGainPlot.processed2.svg'), mode='w') as f:
        p = d.BodeGainPlot()
        preprocess.by_vec_continuous_connectivity_score(p)
        p.title = 'Bode Gain Plot (processed by vec continuous connectivity score)'
        p.figure().savefig(f, format='svg')
    
    print('saved processed plots')

if __name__ == '__main__':
    main()
