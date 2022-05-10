import random
import re
from fuzzingbook.Fuzzer import Fuzzer
from fuzzingbook.GrammarFuzzer import GrammarFuzzer

WHITE_SPACE = ' '
EMPTY_STRING = ''
TXT_FILE = '.txt'
MAKE_DIR = 'mkdir'
from utils.unix_utils import create_directory, create_file_with_random_data


def get_operands_from_command(utility_name, data):
    options = re.findall(pattern=r'-[a-zA-z]* ', string=str(data))
    operands = list()
    # Last operand
    if len(options) != 0:
        last_operand = options[-1]
        idx = data.rfind(last_operand)
        # print("Last operand {0} and {1}, Full string : {2}".format(last_operand,idx, data))
        operand_string = data[idx + len(last_operand):]
        for operand in operand_string.split(WHITE_SPACE):
            re.sub(' +', EMPTY_STRING, operand)
            if operand != EMPTY_STRING:
                operands.append(operand)
    else:
        for operand in data.split(WHITE_SPACE):
            re.sub(' +', EMPTY_STRING, operand)
            if operand != EMPTY_STRING:
                operands.append(operand)

    return operands, set(options), utility_name


def prepare_commands_and_data(operands, execution_id):
    total_operands = len(operands) ** 2
    updated_operands = list()
    # How many combinations are possible for file and directory.
    for idx in range(total_operands + 1):
        binary = str(format(idx, '#010b'))
        # print(binary, idx)
        required_bits = len(operands) * -1
        binary = binary[required_bits:]
        new_operand = list()

        for idx, operand in enumerate(operands):
            if binary[idx] == '1':
                new_operand.append(operand + TXT_FILE)
                create_file_with_random_data(operand + TXT_FILE)
                # print(operand+TXT_FILE)
            else:
                new_operand.append(operand)
                create_directory(operand)
        updated_operands.append(new_operand)
    return updated_operands


class RandomFuzzer:

    def __init__(self, utility_name, execution_id, max_length=32, char_start=32, char_range=32):
        self.utility_name = utility_name
        self.max_length = max_length
        self.char_start = char_start
        self.char_range = char_range
        self.data = list()
        self.execution_id = execution_id

    def fuzz(self):
        result = EMPTY_STRING
        if len(self.data) == 0:
            string_length = random.randrange(0, self.max_length + 1)
            out = EMPTY_STRING
            for i in range(0, string_length):
                out += chr(random.randrange(self.char_start, self.char_start + self.char_range))

            if self.utility_name == MAKE_DIR:
                return self.utility_name + WHITE_SPACE + out

            operands, options, utility_name = get_operands_from_command(self.utility_name, out)
            print(operands, options, utility_name)
            updated_operands = prepare_commands_and_data(operands, self.execution_id)

            for operand in updated_operands:
                command = self.utility_name + WHITE_SPACE + WHITE_SPACE.join(options) + WHITE_SPACE.join(operand)
                self.data.append(command)

        """
        We need to perform some important tasks before returning this information to the runner. 
            Step 1 # Get the operands after the commandline flags.
            Step 2 # Transform the operands to a valid file and directory. 
                -> This is valid only if the target utility is not mkdir.
        """
        if len(self.data) != 0:
            result = self.data.pop()

        return result

    def run(self, runner):
        return runner.run(self.fuzz())


class UnixGrammarFuzzer(GrammarFuzzer):
    def __init__(self, grammar, text_length, utility_name, execution_id):
        super().__init__(grammar)
        self.text_length = text_length
        self.utility_name = utility_name
        self.data = list()
        self.execution_id = execution_id

    def fuzz(self):
        result = WHITE_SPACE
        if len(self.data) == 0:
            result = super(UnixGrammarFuzzer, self).fuzz()

            operands, options, utility_name = get_operands_from_command(self.utility_name, result)
            if self.utility_name == MAKE_DIR:
                print(self.utility_name + WHITE_SPACE + WHITE_SPACE.join(options) + WHITE_SPACE.join(operands))
                return self.utility_name + WHITE_SPACE + WHITE_SPACE.join(options) + WHITE_SPACE.join(operands)

            updated_operands = prepare_commands_and_data(operands, self.execution_id)

            for operand in updated_operands:
                command = self.utility_name + WHITE_SPACE + WHITE_SPACE.join(options) + WHITE_SPACE.join(operand)
                # print(command)
                self.data.append(command)

        """
        We need to perform some important tasks before returning this information to the runner. 
        Step 1 # Get the operands after the commandline flags.
        Step 2 # Transform the operands to a valid file and directory. 
                -> This is valid only if the target utility is not mkdir.
        """
        # result = self.data.pop()
        if len(self.data) != 0:
            result = self.data.pop()

        return result
