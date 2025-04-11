import csv
import math
import pandas
import dataclasses


@dataclasses.dataclass
class Plot:
    x: list[float]
    y: list[float]

class SampleData:
    __dataframe: pandas.DataFrame
    ω: list[float]
    SysGain: list[float]
    SysPhase: list[float]

    def __init__(self, filename: str):
        with open(filename, mode='r') as f:
            self.__dataframe = pandas.DataFrame(
                list(csv.reader(f)),
                index=['ω', 'SysGain', 'SysPhase']
            )
        self.ω = list(map(float, self.__dataframe.loc['ω'].to_list()))
        self.SysGain = list(map(float, self.__dataframe.loc['SysGain'].to_list()))
        self.SysPhase = list(map(float, self.__dataframe.loc['SysPhase'].to_list()))

    def __str__(self):
        return str(self.__dataframe)
    
    def BodeGainPlot(self) -> Plot:
        return Plot(
            x=self.ω,
            y=list(map(lambda x: 20 * math.log10(x), self.SysGain)),
        )
    
    def NyquistPlot(self) -> Plot:
        return Plot(
            x=list(map(lambda x, y: x * math.cos(y), self.SysGain, self.SysPhase)),
            y=list(map(lambda x, y: x * math.sin(y), self.SysGain, self.SysPhase)),
        )
