from importlib import import_module


class Settings(object):

    def __init__(self, db_connector=None, base_folder="", runner=None, log_file="rostam.log"):
        Settings.db_connector = db_connector
        Settings.base_folder = base_folder
        Settings.runner = runner
        Settings.log_file = log_file

    @staticmethod
    def DB_CONNECTOR():
        return Settings.db_connector

    @staticmethod
    def BASE_FOLDER():
        if Settings.base_folder is None:
            return ""
        else:
            return Settings.base_folder

    @staticmethod
    def LOG_FILENAME():
        try:
            return Settings.log_file
        except AttributeError:
            return "rostam.log"

    @staticmethod
    def RUNNER():
        return Settings.runner


class Loader(object):

    @staticmethod
    def class_loader(class_string):
        full_class_string = class_string
        class_data = full_class_string.split(".")
        module_path = ".".join(class_data[:-1])
        class_str = class_data[-1]
        module = import_module(module_path)
        return getattr(module, class_str)
