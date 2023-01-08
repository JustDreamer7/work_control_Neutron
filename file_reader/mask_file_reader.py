import pandas as pd
import pathlib
import datetime

class MaskFileReader:
    def __init__(self, path_to_files):
        self._path_to_files = path_to_files