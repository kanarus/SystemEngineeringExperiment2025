from lib import plot

import csv
import math
import pandas


class SampleData:
    """
    Parsed data from a CSV file containing frequency response data.
    The CSV file should have three float rows:

    1. ω (angular frequency)
    2. System Gain (SysGain)
    3. System Phase (SysPhase)

    sorted by columns in ascending order of ω.

    Methods:

    - `ω`, `SysGain`, `SysPhase`: view the data in the respective rows.
    - `BodeGainPlot`, `NyquistPlot`: generate plot data for Bode Gain or Nyquist plots.
    """

    __dataframe: pandas.DataFrame

    def __init__(self, filename: str):
        with open(filename, mode='r') as f:
            self.__dataframe = pandas.DataFrame(
                csv.reader(f),
                dtype=float,
                index=['ω', 'SysGain', 'SysPhase'],
            ).T.sort_values(
                by='ω',
                ascending=True,
            ) # .T: transpose for pandas's column-oriented data structure

    def __str__(self):
        return str(self.__dataframe)
    
    def ω(self) -> list[float]:
        return self.__dataframe['ω'].to_list()
    
    def SysGain(self) -> list[float]:
        return self.__dataframe['SysGain'].to_list()
    
    def SysPhase(self) -> list[float]:
        return self.__dataframe['SysPhase'].to_list()
    
    def BodeGainPlot(self) -> plot.Plot:
        return plot.Plot(
            x=self.ω(),
            y=list(map(lambda x: 20 * math.log10(x), self.SysGain())),
        )
    
    def NyquistPlot(self) -> plot.Plot:
        return plot.Plot(
            x=list(map(lambda x, y: x * math.cos(y), self.SysGain(), self.SysPhase())),
            y=list(map(lambda x, y: x * math.sin(y), self.SysGain(), self.SysPhase())),
        )
