import argparse
from excav8r import Excva8r
import os
from random import randrange
from datetime import datetime
import piexif


def gallery_as_path_list(path):
    p = []

    for entry in os.listdir(path):
        p.append(f'{path}/{entry}')

    return p


def randomize_mtime(path):
    month = randrange(1,12)
    day = randrange(1,30)
    year = randrange(2000,2020)
    d = datetime(year, month, day, 0, 0)
    epoch = d.timestamp()
    os.utime(path, (epoch, epoch))
    exif_dict = piexif.load(path)
    print(exif_dict)
    new_date = datetime(year, month, day, 0, 0).strftime("%Y:%m:%d %H:%M:%S")
    exif_dict['0th'][piexif.ImageIFD.DateTime] = new_date
    exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = new_date
    exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = new_date
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--keyword', type=str, required=True)
    parser.add_argument('--max', type=int, nargs='?', const=100, default=100)
    parser.add_argument('--dest', type=str, nargs='?', const='./images/gallery/', default='./images/gallery/')
    args = parser.parse_args()

    scraper = Excva8r()
    images = scraper.getDuckDuckGo(args.keyword, max=args.max, as_list=True)

    if not os.path.exists(args.dest):
        os.mkdir(args.dest)

    # randomize image creation data
    for i, image in enumerate(images):
        print(f'{args.dest}{args.keyword.replace(" ","_")}_{i}.jpeg')
        image.convert("RGB")
        image.save(f'{args.dest}{args.keyword.replace(" ","_")}_{i}.jpg')

    for im in gallery_as_path_list(args.dest):
        randomize_mtime(im)
