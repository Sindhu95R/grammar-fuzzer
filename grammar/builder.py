import subprocess
from .unix_grammar import UnixUtilGrammar
from subprocess import CalledProcessError, TimeoutExpired
import sys
from utils.generic_utils import create_cache_directory, CACHE_DIR, DIR_SEPARAROR, TXT_EXTENSION
import re

COMMAND_NOT_FOUND = 'No manual entry'
EMPTY_STRING = ""

pattern_value_map = dict(PATTERN_NAME="NAME", PATTERN_PROLOG="PROLOG", PATTERN_SYNOPSIS="SYNOPSIS",
                         PATTERN_OPTIONS="OPTIONS", PATTERN_DESCRIPTION="DESCRIPTION",
                         PATTERN_EXIT_STATUS="EXIT STATUS", PATTERN_EXAMPLES="EXAMPLES", PATTERN_SEE_ALSO="SEE ALSO",
                         PATTERN_STANDARDS="STANDARDS", PATTERN_HISTORY="HISTORY", PATTERN_BUGS="BUGS",
                         PATTERN_OPERANDS="OPERANDS", PATTERN_INPUT_FILES="INPUT FILES", PATTERN_STDIN="STDIN")


class GrammarBuilder:
    """
    Grammar builder
    This is builder for Grammar for unix utilities by parsing the output from man command.
    """

    def __init__(self, print_on_console=True, generate_file=False) -> None:
        self.print_on_console = print_on_console
        self.generate_file = generate_file

    def build_grammar(self, utility_name):
        grammar = UnixUtilGrammar(utility_name)
        self.build(grammar, utility_name)
        print(grammar.get_grammar())
        return grammar

    def build(self, grammar, utility_name: str):
        man_output = self.execute_man_command(utility_name)
        self.parse_manual(utility_name, grammar)

    def execute_man_command(self, utility_name: str) -> str:
        command = "man -P cat {0}".format(utility_name)
        output = None
        # proc = subprocess.Popen((command,), shell=True)
        try:
            if not create_cache_directory():
                print("Failed in creating the directory for tmp processing", file=sys.stderr)
                return output
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            output = process.stdout.read().decode('utf-8')

            if COMMAND_NOT_FOUND in output or output == EMPTY_STRING or output is None:
                print(" No manual entry for {0}, please install that first".format(command), file=sys.stderr)
                sys.exit(1)

            tmp_file = CACHE_DIR + DIR_SEPARAROR + utility_name + TXT_EXTENSION
            man_output_file = open(tmp_file, 'w')
            man_output_file.write(output)
            man_output_file.close()
            process.kill()
        except CalledProcessError as e:
            print("Failed to get the output from man {0}".format(e))
            sys.exit(1)
        except TimeoutExpired as e:
            print("Timeout happened while executing the man command {0}".format(e))
            sys.exit(1)

        return output

    @staticmethod
    def is_ascii(s):
        try:
            s.decode('ascii')
            return True
        except UnicodeDecodeError:
            return False

    def parse_manual(self, utility_name: str, grammar) -> None:
        tmp_file = CACHE_DIR + DIR_SEPARAROR + utility_name + TXT_EXTENSION
        man_output_file = None
        lines = None
        try:
            man_output_file = open(tmp_file, 'r')
            lines = man_output_file.read()
        except FileNotFoundError as e:
            print("Failed to open the temporary file for man {0}".format(tmp_file))
        finally:
            man_output_file.close()

        """
        Need to move below to a separate function, there is a repetition of code.
        """

        # Lets find the PROLOG for the command.
        start_idx = lines.find(pattern_value_map['PATTERN_PROLOG']) + len(pattern_value_map['PATTERN_PROLOG']) + 1
        end_idx = lines.find(pattern_value_map['PATTERN_NAME']) - 1
        prolog = lines[start_idx: end_idx].lstrip().rstrip()
        prolog = re.sub(' +', ' ', prolog)
        grammar.set_prolog(prolog)

        # Finding the name from the command.
        start_idx = lines.find(pattern_value_map['PATTERN_NAME']) + len(pattern_value_map['PATTERN_NAME']) + 1
        end_idx = lines.find(pattern_value_map['PATTERN_SYNOPSIS']) - 1
        name = lines[start_idx: end_idx].lstrip().rstrip()
        name = re.sub(' +', ' ', name)
        grammar.set_name(name)

        # Finding the synopsis section from the man
        start_idx = lines.find(pattern_value_map['PATTERN_SYNOPSIS']) + len(pattern_value_map['PATTERN_SYNOPSIS']) + 1
        end_idx = lines.find(pattern_value_map['PATTERN_DESCRIPTION']) - 1
        synopsis = lines[start_idx: end_idx].lstrip().rstrip()
        synopsis = re.sub(' +', ' ', synopsis)
        grammar.set_synopsis(synopsis)

        # Finding the description section from the man
        start_idx = lines.find(pattern_value_map['PATTERN_DESCRIPTION']) + len(pattern_value_map['PATTERN_DESCRIPTION']) + 1
        end_idx = lines.find(pattern_value_map['PATTERN_OPTIONS']) - 1
        description = lines[start_idx: end_idx].lstrip().rstrip()
        description = re.sub(' +', ' ', description)
        grammar.set_description(description)

        # Finding the options section from the man
        start_idx = lines.find(pattern_value_map['PATTERN_OPTIONS']) + len(pattern_value_map['PATTERN_OPTIONS']) + 1
        end_idx = lines.find(pattern_value_map['PATTERN_OPERANDS']) - 1
        options = lines[start_idx: end_idx].lstrip().rstrip()
        options = re.sub(' +', ' ', options)
        grammar.set_options(options)

        # Finding the operands section from the man
        start_idx = lines.find(pattern_value_map['PATTERN_OPERANDS']) + len(pattern_value_map['PATTERN_OPERANDS']) + 1
        end_idx = lines.find(pattern_value_map['PATTERN_STDIN']) - 1
        operand = lines[start_idx: end_idx].lstrip().rstrip()
        # operand = re.sub(' +', ' ', operand)
        grammar.set_operand(operand)

