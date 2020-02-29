from secrets import token_bytes
from typing import Optional

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .tmpFile import tmpFile


def textAlign(img: bytes,
              text: str,
              font: Optional[str] = './data/font.otf',
              fontSize: Optional[int] = 100,
              fontColor: Optional[str] = '#FF0000') -> bytes:
    with tmpFile() as tf:
        with open(tf, 'wb') as f:
            f.write(img)
        with Image.open(tf) as im:
            imageFont = ImageFont.truetype(font=font, size=fontSize)
            imageWidth, imageHeight = im.size
            textWidth, textHeight = imageFont.getsize(text)
            imageDraw = ImageDraw.Draw(im)
            textCoordinate = [(imageWidth - textWidth) / 2,
                              (imageHeight - textHeight) / 2]
            imageDraw.text(xy=textCoordinate,
                           text=text,
                           fill=fontColor,
                           font=imageFont)
            im.save(tf, 'PNG')
        with open(tf, 'rb') as f:
            fileRead = f.read()
    return fileRead


def mosaicImage(img: bytes) -> bytes:
    with tmpFile() as tf:
        with open(tf, 'wb') as f:
            f.write(img)
        with Image.open(tf) as im:
            blured = im.filter(ImageFilter.GaussianBlur(radius=10))
            blured.save(tf, 'PNG')
        with open(tf, 'rb') as f:
            fileRead = f.read()
    return fileRead


def convertImageFormat(image: bytes, quality: Optional[int] = 80) -> bytes:
    with tmpFile() as file1, tmpFile() as file2:
        with open(file1, 'wb') as f:
            f.write(image)
        with Image.open(file1) as f:
            f.save(file2, 'BMP')
        with Image.open(file2) as f:
            f.save(file1, 'PNG', optimize=True, quality=quality)
        with open(file1, 'rb') as f:
            readData = f.read()
    return readData + b'\x00' * 16 + token_bytes(16)
