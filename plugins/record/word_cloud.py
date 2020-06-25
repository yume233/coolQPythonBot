from typing import Dict, List

import jieba
from wordcloud import WordCloud

from utils.tmpFile import tmpFile

FONT_PATH = "./data/font.otf"

JIEBA_INIT = False

FreqDict = Dict[str, int]


class WordcloudGenerator:
    def __init__(self):
        global JIEBA_INIT
        if not JIEBA_INIT:
            jieba.initialize()
            jieba.enable_paddle()
            JIEBA_INIT = True

        self._wordcloud = WordCloud(
            font_path=FONT_PATH, width=1920, height=1080, background_color="white"
        )
        self._wordFreqency: FreqDict = {}

    def updateFreqency(self, data: FreqDict) -> FreqDict:
        for k, v in data:
            if k in self._wordFreqency:
                self._wordFreqency[k] += v
            else:
                self._wordFreqency[k] = v
        return self._wordFreqency.copy()

    def update(self, text: str) -> FreqDict:
        cutText: List[str] = jieba.cut(text, use_paddle=True)
        freqDict = self._wordcloud.process_text(" ".join(cutText))
        return self.updateFreqency(freqDict)

    def save(self) -> bytes:
        wordcloud = self._wordcloud.generate_from_frequencies(self._wordFreqency)
        with tmpFile() as tmpFileName:
            wordcloud.to_file(tmpFileName)
            with open(tmpFileName, "rb") as f:
                fileRead = f.read()
        return fileRead
