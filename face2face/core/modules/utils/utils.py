import re
import os
import urllib
from typing import Union
import numpy as np
import cv2

import unicodedata
import glob
from face2face.model_definitions import SWAPPER_MODELS, FACE_ENHANCER_MODELS
from media_toolkit import ImageFile


def load_image(img: str, np.array, ImageFile):
    try:
        image = ImageFile().from_any(img).to_np_array()
        # convert to cv2 BGR image
        # case 4 channels
        if len(image.shape) == 3 and image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
        # case 1 channel
        elif len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    except Exception as e:
        raise ValueError(f"Could not load image {img}. Error: {e}")

    return image


def encode_path_safe(filename: str, allow_unicode=False):
    """
    Makes a string path safe by removing / replacing not by the os allowed patterns.
    This converts:
    spaces 2 dashes, repeated dashes 2 single dashes, remove non alphanumerics, underscores, or hyphen, string 2 lowercase
    strip
    """
    filename = str(filename)
    if allow_unicode:
        filename = unicodedata.normalize('NFKC', filename)
    else:
        filename = (
            unicodedata.normalize('NFKD', filename)
            .encode('ascii', 'ignore')
            .decode('ascii')
        )
    filename = re.sub(r'[^\w\s-]', '', filename.lower())
    return re.sub(r'[-\s]+', '-', filename).strip('-_')


def get_files_in_dir(path: str, extensions: list | str = None):
    """returns all files in a directory filtered by extension list"""
    if not os.path.isdir(path):
        print(f"{path} is not a directory. Returning empty list")
        return []

    files = []
    if extensions is None:
        # return all files
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    else:
        # return files filtered by extensions
        if extensions is str:
            extensions = [extensions]
        for ext in extensions:
            files.extend(glob.glob(os.path.join(path, "*" + ext)))

    return files


def download_file(download_url: str, save_path: str):
    model_dir = os.path.dirname(save_path)
    if not os.path.isdir(model_dir):
        os.makedirs(model_dir, exist_ok=True)

    if not os.path.isfile(save_path):
        print(f'Downloading {download_url}')
        urllib.request.urlretrieve(download_url, save_path)
        print(f'Downloaded {download_url}')
    return save_path


def download_model(model_name: str):
    """
    Download the models specified in the download urls
    :param model_name: name of the model to download. Look into model_definitions.py for available models
    :return: path to the downloaded model
    """
    # get model config
    model_config = SWAPPER_MODELS.get(model_name, None)
    if model_config is None:
        model_config = FACE_ENHANCER_MODELS.get(model_name, None)
    if model_config is None:
        raise ValueError(f"Model {model_name} not found")

    # download model
    download_url = model_config.get('url', None)
    save_path = model_config.get('path', None)
    return download_file(download_url, save_path)

