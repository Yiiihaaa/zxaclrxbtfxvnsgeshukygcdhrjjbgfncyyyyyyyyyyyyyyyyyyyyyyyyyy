import os
import shutil


def __autoclean(path=(os.getcwd())):
    """
    Helper function to get all "__pycache__" folders
    :return: A list of paths with name __pycache__
    """
    if os.path.isdir(path) and '__pycache__' in path:
        return [path]
    elif os.path.isfile(path):
        return []
    else:
        res = []
        for file_name in os.listdir(path):
            subitem = os.path.join(path, file_name)
            res += __autoclean(subitem)
        return res


def autoclean():
    """
    Cleans all Python cache.
    """
    for path in __autoclean():
        shutil.rmtree(path, ignore_errors=True)