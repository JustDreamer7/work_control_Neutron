from abc import ABCMeta, abstractmethod
import pathlib


class FileReader(metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, path_to_files):
        self._path_to_files = path_to_files
        self._file_name = None
        self._columns = None

    @property
    @abstractmethod
    def path_to_files(self):
        return self._path_to_files

    @property
    @abstractmethod
    def file_name(self):
        return self._file_name

    @property
    @abstractmethod
    def columns(self):
        return self._columns

    @abstractmethod
    def making_file_path(self, file_directory):
        file_path = pathlib.PurePath(self.path_to_files, file_directory, self.file_name)
        return file_path

    @abstractmethod
    def reading_file(self):
        pass

    @classmethod
    def __subclasshook__(cls, class_name):
        if cls is FileReader:
            for class_ in class_name.__mro__:
                if (
                        "reading_file" in class_.__dict__
                        and callable(class_.__dict__["reading_file"])
                ):
                    return True
        return NotImplemented
