import os

CACHE_DIR = 'tmp_cache'
DIR_SEPARAROR = '/'
TXT_EXTENSION = ".txt"

def create_cache_directory():
    result = True
    try:
        if not os.path.exists(CACHE_DIR):
            os.mkdir(CACHE_DIR)
            print("Cache directory has been created Path -> {0}".format(CACHE_DIR))
        else:
            print("Cache directory -> {0} already exists".format(CACHE_DIR))
    except FileExistsError:
        result = False

    return result
