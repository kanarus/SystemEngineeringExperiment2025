import csv
from pandas import DataFrame


class SampleData:
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
    