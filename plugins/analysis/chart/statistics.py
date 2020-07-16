from typing import Any, Dict

import seaborn as sns
from pandas import DataFrame

from utils.tmpFile import tmpFile


class DataFrameMaker:
    def __init__(self, index: Dict[str, object]):
        self._index = index
        self._frame = DataFrame(index=[*index.keys()])

    def update(self, data: Dict[str, Any]) -> int:
        frameData = {k: data[k] for k in self._index.keys()}
        self._frame = self._frame.append(frameData, ignore_index=True)
        return self._frame.size

    def read(self) -> DataFrame:
        return self._frame


class Chart:
    @staticmethod
    def _toImage(grid: sns.FacetGrid) -> bytes:
        with tmpFile(ext=".png") as tmpFileName:
            grid.savefig(tmpFileName)
            with open(tmpFileName, "rb") as f:
                fileRead = f.read()
        return fileRead

    @classmethod
    def chatFrequency(cls, data: DataFrame):
        assert "date" in data
        assert "time" in data
        grid = sns.FacetGrid(data=data, row="date", aspect=2)
        grid.map(sns.distplot, "time", rug=True, kde=True)
        return cls._toImage(grid)
