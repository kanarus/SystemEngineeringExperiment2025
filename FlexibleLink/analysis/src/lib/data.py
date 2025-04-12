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

    The data is automatically sorted by ω in ascending order when loaded.

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
    
    def SimplePlot(self) -> plot.Plot:
        return plot.Plot(
            x=self.ω(),
            y=self.SysGain(),
            title='Simple Plot',
            xlabel='ω [rad/sec]',
            ylabel='G(jω)',
        )

    def BodeGainPlot(self) -> plot.Plot:
        return plot.Plot(
            x=self.ω(),
            y=list(map(lambda x: 20 * math.log10(x), self.SysGain())),
            title='Bode Gain Plot',
            xlabel='ω [rad/sec]',
            ylabel='20log|G(jω)|',
            xlogscale=True,
        )
    
    def NyquistPlot(self) -> plot.Plot:
        return plot.Plot(
            x=list(map(lambda x, y: x * math.cos(y), self.SysGain(), self.SysPhase())),
            y=list(map(lambda x, y: x * math.sin(y), self.SysGain(), self.SysPhase())),
            title='Nyquist Plot',
            xlabel='Re(G(jω))',
            ylabel='Im(G(jω))',
        )
    

"""

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
            x=self.__data.ω(),
            y=self.__data.SysGain(),
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

"""
