import whatimage
import io
from PIL import Image
import pillow_heif

def decode_heic(path):
    heif_file = pillow_heif.read_heif(path)
    img = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
    )

    return img
