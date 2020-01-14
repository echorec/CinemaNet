from PIL import Image
from glob import glob
from pathlib import Path
from typing import Union, Optional
import os
import argparse

parser = argparse.ArgumentParser(
    description='''
    ============================================================================
                 Reduce Image File Sizes While Preserving Quality
    ============================================================================

    This script uses PIL to scan a directory for image files recursively and
    reduce the size of images that are larger than the `size_threshold`,
    while preserving its quality.
    Optionally, you can resize images with/without preserving its aspect ratio.

    Defaults
    --------
    * aspect ratio is preserved. You can change this by passing in
      'False' for the `keep_aspect_ratio` argument
    * images are not resized.
          - If preserving aspect ratio, you can change
            this by either passing in a `scale_factor` or just the `height`
            argument. If you pass both, `scale_factor` is given preference.
          - If not preserving aspect ratio, enter 'False' for the
            `keep_aspect_ratio` argument and enter the desired `height`
            and `width` arguments
    * images larger than 1.4 MBs are optimised. You can change this by
      passing in the `size_threshold` argument

    The script isn't optimised for speed, so expect a long runtime.

    Examples
    --------

    python optimise-image-size.py --path ~/dataset

    python optimise-image-size.py \
        --path ~/dataset          \
        --size_threshold 1.0      \
        --keep_aspect_ratio False \
        --height 1080             \
        --width 1920

    python optimise-image-size.py \
        --path ~/dataset          \
        --size_threshold 1.0      \
        --keep_aspect_ratio True  \
        --scale_factor 0.75
    ''', formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('--path', type=str, required=True,
                    help='')
# TODO --> Make suffix work
# parser.add_argument('--suffix', type=str, required=False,
#                     default='_opt',
#                     help='')
parser.add_argument('--size_threshold', type=float, required=False,
                    default=1.3,
                    help='')
parser.add_argument('--scale_factor', type=float, required=False,
                    default=1.,
                    help='')
parser.add_argument('--width', type=float, required=False,
                    default=None,
                    help='')
parser.add_argument('--height', type=float, required=False,
                    default=None,
                    help='')
parser.add_argument('--quality', type=float, required=False,
                    default=85,
                    help='')
parser.add_argument('--keep_aspect_ratio', type=bool, required=False,
                    default=True,
                    help='')

args = parser.parse_args()
# TODO --> Make suffix work, accept as CL arg
args.suffix=''

def resize_img(fname: Union[str, Path],
               scale_factor: float=1.,
               keep_aspect_ratio: bool = True,
               width:    Optional[int] = None,
               height:   Optional[int] = None):
    '''
    Resize an Image with PIL

    If you'd like to maintain aspect ratio, enter either
    `height` or `scale_factor`. If you enter both, `scale_factor`
    will apply.

    Returns a PIL `Image`
    *
    '''
    img = Image.open(fname)
    w,h = img.size

    if keep_aspect_ratio:
        assert width is None, 'If preserving aspect ratio, enter base height only'
        assert height or scale_factor, 'Enter `height` or `scale_factor`'
        if width is None and height is not None: width = int(height * w/h)
        if scale_factor is not None:
            height = int(h * scale_factor)
            width  = int(w * scale_factor)
        img = img.resize((width, height), Image.LANCZOS)
    else:
        if scale_factor is not None: print('`scale_factor` is irrelevant if not preserving aspect ratio')
        if width and height: img = img.resize((width, height), Image.LANCZOS)
        else: img.resize(img.size, Image.LANCZOS)
    return img

flatten = lambda l: [item for sublist in l for item in sublist]
def get_fnames(path: Union[str,Path],
               exts: list = ['jpg', 'JPG', 'png', 'PNG', 'tiff', 'TIFF', 'jpeg', 'JPEG']):
    'Recursively get filenames with `exts` extensions in the `path`'
    files=[list(Path(path).rglob(f'*.{ftype}')) for ftype in exts]
    return flatten(files)

def optimise_images(path: Union[str,Path], quality:int=85, suffix:str='',
                    size_threshold: Union[int,float]=1.5,
                    scale_factor: float=1.,
                    keep_aspect_ratio: bool = True,
                    width:    Optional[int] = None,
                    height:   Optional[int] = None):
    '''
    Reduce image filesizes. Optionally, resize them.
    If suffix='', the files will be replaced
    '''
    files      = get_fnames(path)
    mb_divisor = (1000*1000.)
    for f in files:
        fsize = os.path.getsize(f) / mb_divisor
        if fsize > size_threshold:
            print(f'Optimising {f}')
            img = resize_img(f, scale_factor, keep_aspect_ratio, width, height)
            img.save(f'{f}', quality=quality, optimize=True)
            print(f'{fsize:.2f} MB --> {(os.path.getsize(f) / mb_divisor):.2f} MB')
            print()

optimise_images(args.path, args.quality, args.suffix,
                args.size_threshold, args.scale_factor,
                args.keep_aspect_ratio, args.width,
                args.height)
