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

    def __init__(self, filename: str):
        with open(filename, mode='r') as f:
            self.__dataframe = pandas.DataFrame(
                csv.reader(f),
                dtype=float,
                index=['ω', 'SysGain', 'SysPhase'],
            )

    def __str__(self):
        return str(self.__dataframe)
    
    def ω(self) -> list[float]:
        return self.__dataframe.loc['ω'].to_list()
    
    def SysGain(self) -> list[float]:
        return self.__dataframe.loc['SysGain'].to_list()
    
    def SysPhase(self) -> list[float]:
        return self.__dataframe.loc['SysPhase'].to_list()
    
    def BodeGainPlot(self) -> Plot:
        return Plot(
            x=self.ω(),
            y=list(map(lambda x: 20 * math.log10(x), self.SysGain())),
        )
    
    def NyquistPlot(self) -> Plot:
        return Plot(
            x=list(map(lambda x, y: x * math.cos(y), self.SysGain(), self.SysPhase())),
            y=list(map(lambda x, y: x * math.sin(y), self.SysGain(), self.SysPhase())),
        )
    
    # def eliminate(self, )
    

