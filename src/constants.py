import os

VERSION_REGEX = r"^\d+\.\d+\.\d+(-(alpha|beta|rc)\.\d+)?$"
PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
VERSION = "0.1.0"
NAME = "ivy-seed"
IVY_ROOT_DIR = os.path.join(os.path.expanduser('~'), "Documents", NAME)
