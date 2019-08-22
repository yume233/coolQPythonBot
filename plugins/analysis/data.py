import csv
import os
import re
import sqlite3
from secrets import token_bytes

import jieba
from nonebot import NoneBot, get_bot
from PIL import Image
from wordcloud import WordCloud

from utils.customDecorators import Sync
from utils.customObjects import SyncWrapper

from .tmpFile import tmpFile

MATCH = re.compile(r'\[CQ:.+\]')


async def _getinfo():
    bot = get_bot()
    botQQ = await bot.get_login_info()
    programPath = await bot.get_version_info()
    return botQQ['user_id'], programPath['coolq_directory']


def _convertToPNG(imageRes: bytes) -> bytes:
    with tmpFile() as readName, tmpFile() as writeName:
        with open(readName, 'wb') as f:
            f.write(imageRes)
        with Image.open(readName) as img:
            img.save(writeName, 'PNG')
        with open(writeName, 'rb') as f:
            fileRead = f.read()
    fileHashChanged = fileRead + b'\x00' * 16 + token_bytes(16)
    return fileHashChanged


_getinfo = Sync(_getinfo)


def genWordCloud(id: int, type: str) -> bytes:
    botQQ, programPath = _getinfo()
    databasePath = os.path.join(programPath, f'./data/{botQQ}/eventv2.db')
    #print(databasePath)
    conn = sqlite3.connect(databasePath)
    cursor = conn.execute(
        '''SELECT "group","account","content" FROM "event" WHERE type != 2001'''
    )
    with tmpFile(ext='.csv') as tmp:
        headers = ['group', 'account', 'content']
        with open(tmp, 'wt', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for i in cursor:
                i = [t.replace('\0', '') for t in i]
                writer.writerow(i)
        conn.close()
        cutList = []
        with open(tmp, 'rt', encoding='utf-8') as f:
            s = f'qq/{type}/{id}'
            reader = csv.DictReader(f)
            for i in reader:
                if (i['group'] != s) and (i['account'] != s):
                    continue
                cutWord = jieba.cut(MATCH.sub('',i['content']))
                cutList.extend(cutWord)
    cutText = ' '.join(cutList)
    cloud = WordCloud(font_path=os.path.join(
        os.path.split(__file__)[0], 'font.otf'),
                      width=1920,
                      height=1080,
                      background_color='white',
                      max_font_size=400).generate(cutText)
    with tmpFile(ext='.jpg') as tmp:
        cloud.to_file(tmp)
        with open(tmp, 'rb') as f:
            bytesRead = f.read()
    return _convertToPNG(bytesRead)
