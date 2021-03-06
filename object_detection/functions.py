import math
import numpy as np
import random
from typing import Union
from operator import itemgetter

# from PIL import Image
from matplotlib.colors import CSS4_COLORS
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from .preprocess import Image

RANDOM_COLORS = list((CSS4_COLORS.keys()))
random.shuffle(RANDOM_COLORS)


def filter_predict(detection: dict, name: list):
    if not name:
        return detection
    filtered_detection = dict()

    filtered_list = [
        i for i, d in enumerate(detection["detection_classes"]) if d["name"] in name
    ]
    if not filtered_list:
        return filtered_detection

    for key in detection.keys():
        if not hasattr(detection[key], "__getitem__"):
            filtered_detection[key] = detection[key]
        else:
            filtered_detection[key] = [detection[key][index] for index in filtered_list]
            # filtered_detection[key] = itemgetter(*filtered_list)(detection[key])
    return filtered_detection


def cut_threshold(detection: dict, threshold: float = math.inf, count: int = math.inf):
    filtered_detection = dict()
    if not detection:
        return filtered_detection
    # elif not hasattr(detection["detection_scores"], "__iter__"):
    #     if detection["detection_scores"] < threshold:
    #         return filtered_detection
    #     else:
    #         return detection

    score_list = [
        i for i, d in enumerate(detection["detection_scores"]) if d >= threshold
    ]
    if score_list:
        max_score = max(score_list)
    else:
        max_score = -1

    n_threshold = min(count, max_score)
    for key in detection.keys():
        if not hasattr(detection[key], "__getitem__"):
            filtered_detection[key] = detection[key]
        else:
            filtered_detection[key] = detection[key][: n_threshold + 1]

    return filtered_detection


def get_object_patch(img: Image, predict: dict, **kwargs):

    height, width, _ = img.size

    patch_list = list()
    if not predict:
        return patch_list
    # if not isinstance(predict['detection_scores'],tuple):
    #     for key in predict.keys():
    #         predict[key] = tuple(predict[key])

    for box, cls, color in zip(
        predict["detection_boxes"], predict["detection_classes"], RANDOM_COLORS
    ):
        if not isinstance(cls, dict) or "name" not in cls:
            label = None
        else:
            label = cls["name"]
        y_min, x_min, y_max, x_max = box
        x_delta = width * (x_max - x_min)
        y_delta = height * (y_max - y_min)
        patch = patches.Rectangle(
            (width * x_min, height * y_min),
            x_delta,
            y_delta,
            fill=False,
            label=label,
            linewidth=1,
            color=color,
        )
        patch_list.append(patch)
    return patch_list


def plot_object_detection(img: Image, predict: dict, **kwargs):

    fig, ax = plt.subplots(**kwargs)
    ax.imshow(img.array)

    patch_list = get_object_patch(img, predict, **kwargs)
    for patch in patch_list:
        ax.add_patch(patch)

    ax.legend()

    plt.show()
