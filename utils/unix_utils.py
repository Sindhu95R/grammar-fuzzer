import subprocess
import os
from base64 import b64encode
import random
import sys


def execute_command(input_command: str) -> dict:
    execution_result = {'exit code': None, 'output': None}
    try:
        process = subprocess.Popen(input_command, shell=True, stdout=subprocess.PIPE)
        output = process.communicate()[0]
        execution_result['exit code'] = process.returncode
        execution_result['output'] = output.decode('utf-8')
    except UnicodeDecodeError as e:
        execution_result = {'exit code': 999, 'output': 'Exception happened while decoding the output'}
    except OSError as e:
        execution_result = {'exit code': 999, 'output': str(e)}

    return execution_result


def create_file_with_random_data(file_name, max_length=1000):
    random_file = None
    max_length = random.randint(max_length, max_length * 100)
    try:
        random_file = open(file_name, 'w')
        random_bytes = os.urandom(max_length)
        token = b64encode(random_bytes).decode('utf-8')
        random_file.write(token)
    except FileNotFoundError:
        pass
    except MemoryError as e:
        print("Memory error happened while creating file {0}".format(file_name), file=sys.stderr)
    except IsADirectoryError as e:
        print("Operation performed on directory is not allowed {0}".format(file_name), file=sys.stderr)
    finally:
        if random_file:
            random_file.close()


def create_directory(directory_name):
    result = True
    try:
        if not os.path.exists(directory_name):
            os.mkdir(directory_name)
    except FileExistsError:
        result = False
    except FileNotFoundError:
        result = False
    except NotADirectoryError:
        result = False

    return result


if __name__ == '__main__':
    # Example
    # create_file_with_random_data('random.txt', path='../tmp_cache/')
    # print(execute_command('echo hello')) # {'exit code': 0, 'output': 'hello\n'}
    pass
