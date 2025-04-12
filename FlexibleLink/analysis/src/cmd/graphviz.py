from lib.data import SampleData
from lib.plot import Plot

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

    # create a preprocessed Bode Gain plot, where
    # outliers are removed and the data is smoothed

    # by invariant of `Plot` class, the data points in `p`
    # are sorted in ascending order of x (ω)
    p: Plot = d.BodeGainPlot()

    i = 2 # assume the first two points (index 0, 1) are not outliers
    while i < p.size():
        this, prev1, prev2 = p.get(i), p.get(i-1), p.get(i-2)

        # Compare the angles of two vectors:
        # 
        # - `prev_vec` : prev2 -> prev1
        # - `this_vec` : prev1 -> this
        # 
        # If the difference of the angles is greater than a threshold,
        # (i.e. the angle is not continuous, this poits makes a non-smooth part)
        # there's two possibilities:
        # 
        # 1. this point is an outlier
        # 2. this is the first point of a new curve
        # 
        # When 1., we remove this point.
        # When 2., we keep this point and go to the next point.

        THRESHOLD_RADIANS = math.pi / 8 # [rad], 22.5 degrees

        prev_vec_radians = math.atan2(prev1.y - prev2.y, prev1.x - prev2.x)
        this_vec_radians = math.atan2(this.y - prev1.y, this.x - prev1.x)
        
        if abs(this_vec_radians - prev_vec_radians) < THRESHOLD_RADIANS:
            i += 1
        else:
            # Check if this point is an outlier (case 1.).
            # 
            # 1. When `this` is the final point of the curve,
            #    `this` will be an outlier and we should remove `this`.
            # 2. When `this` is NOT the final point of the curve,
            #    we introduce `next`, the next point of `this`, and:
            #    
            #    - `next_vec` : this -> next
            #    - `skip_vec` : prev1 -> next
            #    
            #    a. If the angle of `skip_vec` is continuous with `prev_vec`,
            #       `this` can be considered as an outlier.
            #    b. If the angle of `skip_vec` is NOT continuous with `prev_vec`,
            #
            #        p. If the angle of `next_vec` is continuous with `this_vec`,
            #           `this`, `next`, `next2` will be the first points of a new curve.
            #        q. If the angle of `next_vec` is NOT continuous with `this_vec`,
            #           we introduce `next2`, the next point of `next` (if cannot,
            #           i.e. `next` is the final point of the curve, we can consider
            #           both `this` and `next` as outliers, and remove them), and:
            #
            #           - `next2_vec` : next -> next2
            #           - `skip2_vec` : this -> next2
            #           
            #           x. If the angle of `skip2_vec` is continuous with `this_vec`,
            #              `this` and `next2` will be the first points of a new curve,
            #              and `next` will be an outlier.
            #           y. If the angle of `skip2_vec` is NOT continuous with `this_vec`,
            #              
            #              - If `skip2_vec` is continuous with `next_vec`,
            #                `next` and `next2` will be the first points of a new curve,
            #                and `this` will be an outlier.
            #              - If `skip2_vec` is NOT continuous with `next_vec`,
            #                go to the next point.

            if i == p.size() - 1:
                p.drop(i)
            else:
                next = p.get(i + 1)

                skip_vec_radians = math.atan2(next.y - prev1.y, next.x - prev1.x)
                next_vec_radians = math.atan2(next.y - this.y, next.x - this.x)

                if abs(skip_vec_radians - prev_vec_radians) < THRESHOLD_RADIANS:
                    p.drop(i) # `this` is an outlier
                    i += 1    # skip `next`, obviously not an outlier because of the continuity
                elif abs(next_vec_radians - this_vec_radians) < THRESHOLD_RADIANS:
                    i += 2    # skip `this` and `next`, both are the first points of a new curve
                else:
                    if i == p.size() - 2:
                        p.drop(i) # `this` is an outlier
                        p.drop(i) # `next` is an outlier
                    else:
                        next2 = p.get(i + 2)

                        skip2_vec_radians = math.atan2(next2.y - this.y, next2.x - this.x)
                        next2_vec_radians = math.atan2(next2.y - next.y, next2.x - next.x)

                        if abs(skip2_vec_radians - this_vec_radians) < THRESHOLD_RADIANS:
                            p.drop(i + 1) # `next` is an outlier
                            i += 2        # skip `next2`, obviously not an outlier because of the continuity
                        elif abs(skip2_vec_radians - skip_vec_radians) < THRESHOLD_RADIANS:
                            p.drop(i) # `this` is an outlier
                            i += 2    # skip `next` and `next2`, both are the first points of a new curve
                        else:
                            i += 1 # go to the next point

    with open(path.join(save_dir, 'BodeGainPlot.processed.svg'), mode='w') as f:
        p.figure().savefig(f, format='svg')
    
    print('saved processed plot')

if __name__ == '__main__':
    main()
