import re
from fuzzingbook.Grammars import def_used_nonterminals
NONE_OPERAND = "       None."
PATTERN_FILE_NAME = "file"
PATTERN_DIR_NAME = "dir"


class UnixUtilGrammar:
    def __init__(self, utility_name):
        self.utility_name = utility_name
        self.name = None
        self.prolog = None
        self.synopsis = None
        self.exit_status = None
        self.examples = None
        self.description = None
        self.options = None
        self.operand = None
        self.mandatory_params = dict()
        self.optional_params = list()
        self.grammar = None

    def __str__(self) -> str:
        message = self.utility_name + "\n"
        message += "Mandatory parameter : \n"
        for key, value in self.mandatory_params:
            message += "Param : " + key + " -> " + value + "\n"

        message += "Optional parameter : \n"
        for key, value in self.mandatory_params:
            message += "Param : " + key + " -> " + value + "\n"

        return message

    def set_prolog(self, prolog):
        self.prolog = prolog

    def set_synopsis(self, synopsis):
        cleaned_synopsis = list()
        append_from_last = False
        last = ""
        for single_synopsis in synopsis.split('\n'):
            if not single_synopsis.lstrip().rstrip() == '':
                if single_synopsis.lstrip().rstrip().endswith('\\'):
                    append_from_last = True
                    last += single_synopsis.lstrip().rstrip()
                else:
                    if append_from_last:
                        last += single_synopsis.lstrip().rstrip()

                        cleaned_synopsis.append(last.replace('\\', ''))
                        append_from_last = False
                        last = ""
                    else:
                        cleaned_synopsis.append(single_synopsis.lstrip().rstrip())
        self.synopsis = cleaned_synopsis

    def set_exit_status(self, exit_status):
        self.exit_status = exit_status

    def set_examples(self, examples):
        self.examples = examples

    def set_name(self, name):
        self.name = name

    def set_description(self, description):
        self.description = description

    def set_options(self, options):
        self.options = options
        # Better prepare here a list to use in grammar
        for option in re.findall(pattern=r'-[a-zA-z] ', string=str(self.options)):
            self.optional_params.append(option)
        self.optional_params.append("")

    def set_operand(self, operand):
        self.operand = operand

    def internal_grammar(self):
        grammar = dict()
        grammar["<alphabets>"] = list()
        for asscii_code in range(97, 123):
            grammar["<alphabets>"].append(chr(asscii_code ^ 32))
            grammar["<alphabets>"].append(chr(asscii_code))

        grammar["<digits>"] = list()
        for idx in range(0, 11):
            grammar["<digits>"].append(str(idx))

        grammar["<special>"] = list()
        for idx in range(33, 65):
            grammar["<special>"].append(chr(idx))

        grammar["<letter>"] = ["<alphabets>", "<digits>", "<special>"]
        grammar["<string>"] = ["<letter>", "<letter><string>"]
        grammar["<file>"] = ["<string>"]
        grammar["<dir>"] = ["<string>"]

        return grammar

    def find_best_match(self, target: str):
        if "FILE" in target.upper():
            grammar = self.internal_grammar_str()
            grammar = dict()
            grammar["<file>"] = ["<string>"]
            return grammar

    def get_grammar(self):
        # Grammar is already generated, lets return it
        if self.grammar is not None:
            return self.grammar

        grammar = dict()
        grammar["<start>"] = ["<command>"]
        grammar["<options>"] = list()
        grammar["<operands>"] = list()

        # Lets parse the options from synopsis
        prepare_options = False
        for syn in self.synopsis:
            for options in re.findall(r"\[(.*?)\]", syn):
                if options.startswith('-') or '-' in options:
                    prepare_options = True
                    for single_option in options.split('|'):
                        if len(single_option.split(" ")) == 1:
                            grammar["<options>"].append(single_option)

        # Two command line arguments can be combined as well.
        if prepare_options:
            grammar["<options>"].append(" <options> <options> ")

        operators_feature = dict()
        for idx, syn in enumerate(self.synopsis):
            # Checking if the operand is between []
            for operand in re.findall(r"\[(.*?)\]", syn):
                if not operand.startswith('-') or '-' not in operand:
                    if idx in operators_feature:
                        operators_feature[idx].append(operand)
                    else:
                        operators_feature[idx] = [operand]

            # Lets find index of "]" and the command itself, whatever will be max, that will be used
            # to get the operands for the command.
            idx_right_bracket = syn.rfind(']')
            idx_command = syn.rfind(self.utility_name)
            operand_idx = max(idx_command, idx_right_bracket)
            operand_str = syn[operand_idx:]
            operand_str = operand_str.replace(']', '')
            for operand in operand_str.split(" "):
                if idx in operators_feature:
                    operators_feature[idx].append(operand)
                else:
                    operators_feature[idx] = [operand]

        command = "<utility_name>"

        # Lets prepare the grammar for the <command>
        if prepare_options:
            command += " <options> "

        # There are operands for which grammar needs to be generated.
        if len(operators_feature) > 0:
            command += " <operands> "

            operand_list = grammar["<operands>"]
            idx = 0
            for key, value in operators_feature.items():
                for operand in value:
                    if 'FILE' in operand.upper():
                        # That means the index already exists, add to the operands
                        if len(operand_list) >= idx + 1:
                            temp_grammar = operand_list[idx]
                            temp_grammar += " <file>"
                            operand_list[idx] = temp_grammar
                        else:
                            operand_list.insert(idx, "<file>")
                    elif 'DIR' in operand.upper():
                        if len(operand_list) >= idx + 1:
                            temp_grammar = operand_list[idx]
                            temp_grammar += " <dir>"
                            operand_list[idx] = temp_grammar
                        else:
                            operand_list.insert(idx, "<dir>")
                    elif 'STRING' in operand.upper():
                        if len(operand_list) >= idx + 1:
                            temp_grammar = operand_list[idx]
                            temp_grammar += " <string>"
                            operand_list[idx] = temp_grammar
                        else:
                            operand_list.insert(idx, "<string>")

                idx += 1

        grammar["<command>"] = [command]
        grammar["<utility_name>"] = [self.utility_name]

        for key, value in self.internal_grammar().items():
            grammar[key] = value

        # Make the grammar correct before sending it back.
        defined_nonterminals, used_nonterminals = def_used_nonterminals(grammar)
        not_used_terminals = defined_nonterminals - used_nonterminals
        for unused_item in not_used_terminals:
            del grammar[unused_item]

        self.grammar = grammar
        return self.grammar

