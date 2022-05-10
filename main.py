"""
file: main.py
This will be the driver program for the fuzzers.
"""
from grammar.builder import GrammarBuilder
from datetime import datetime
import os
import sys
from prettytable import PrettyTable
from fuzzers.Fuzzer import UnixGrammarFuzzer, RandomFuzzer
from fuzzers.runner import ProgramRunner
from junit_xml import TestSuite, TestCase, to_xml_report_file
from fuzzers.fuzzingreport import UnixFuzzerReport as Report
import json
from utils.unix_utils import execute_command, create_directory
import time

VALID_FUZZERS = ["RANDOM", "GRAMMAR"]
TEST_CASE_EXTENSION = '.test'
PASS = "PASS"
FAIL = "FAIL"
UNRESOLVED = "UNRESOLVED"
DOT = '.'
REPORT_DIR = 'report/'
REPORT_NAME = 'junit_fuzzing_report.xml.txt'
REPORT_NAME_FINAL = 'junit_fuzzing_report.xml'


def add_test_to_report(execution_result, test_cases, test_case_index, utility_name):
    (result, utility_output, utility_input) = execution_result

    report_name = utility_name + str(test_case_index) + TEST_CASE_EXTENSION
    report = Report(report_name)
    report.add('utility_name', utility_name)
    report.add('result', result)
    report.add('utility_input', utility_input)

    if utility_output == PASS:
        report.set_status(Report.PASSED)
    elif utility_output == FAIL:
        report.set_status(Report.FAILED)
    else:
        # If status is not known, lets put pass at that moment.
        report.set_status(Report.PASSED)

    # Lets start with generating the test case from the report.
    if report.get_status() != Report.PASSED:
        test_case = TestCase(name=report.get_name(), status=report.get_status())
        test_case.add_failure_info(message=json.dumps(report.to_dict()))
        test_cases.append(test_case)
    else:
        test_case = TestCase(name=report.get_name(), status='Pass', stdout=json.dumps(report.to_dict()))
        test_cases.append(test_case)


def save_report(test_cases):

    try:
        if not os.path.exists(os.path.dirname(REPORT_DIR)):
            try:
                os.makedirs(os.path.dirname(REPORT_DIR))
            except OSError:
                pass
        with open(REPORT_DIR + REPORT_NAME, 'w') as report_file:
            to_xml_report_file(report_file, [TestSuite("Fuzzer - Test Suite", test_cases)], prettyprint=True)
    except Exception as e:
        print('Failed to save report "{}" to {} because: {}'
              .format(REPORT_NAME, REPORT_DIR, e))

    os.rename(REPORT_DIR + REPORT_NAME, REPORT_DIR + REPORT_NAME_FINAL)

def load_env_variables() -> dict:
    # Mandatory environment variables.
    env_keys = dict()
    try:
        env_keys['TARGET_UTILITY'] = os.environ['TARGET_UTILITY']
        env_keys['FUZZER_TYPE'] = os.environ['FUZZER_TYPE']
        if env_keys['FUZZER_TYPE'] not in VALID_FUZZERS:
            raise ValueError("Please check 'FUZZER_TYPE', it could have only {0} ".format(VALID_FUZZERS))
    except KeyError as e:
        print("Please set all the required environment variables {0}".format(e), file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(e)
        sys.exit(1)

    # Optional variables, if not passed
    if 'FUZZER_ITERATION' in os.environ:
        env_keys['FUZZER_ITERATION'] = int(os.environ['FUZZER_ITERATION'])
    else:
        env_keys['FUZZER_ITERATION'] = 100

    if 'TIME_OUT' in os.environ:
        env_keys['TIME_OUT'] = int(os.environ['TIME_OUT'])
    else:
        env_keys['TIME_OUT'] = 5

    if 'RANDOM_FILE_CHAR_LENGTH' in os.environ:
        env_keys['RANDOM_FILE_CHAR_LENGTH'] = int(os.environ['RANDOM_FILE_CHAR_LENGTH'])
    else:
        env_keys['RANDOM_FILE_CHAR_LENGTH'] = 1000

    # Print variables
    print("Starting the fuzzer with below configuration", file=sys.stdout)
    table = PrettyTable(border=True, header=True, padding_width=1,
                        field_names=["Parameter", "Value"])

    for k, v in env_keys.items():
        table.add_row([k, v])

    print(table, file=sys.stdout)
    sys.stdout.flush()

    return env_keys


def main():
    env_keys = load_env_variables()
    test_cases_list = list()
    now = datetime.now()
    execution_id = now.strftime("%m%d%Y_%H%M%S") + '_' + env_keys['TARGET_UTILITY']

    if env_keys['FUZZER_TYPE'] == 'GRAMMAR':
        grammar = GrammarBuilder().build_grammar(env_keys['TARGET_UTILITY'])
        fuzzer = UnixGrammarFuzzer(grammar.get_grammar(), env_keys['RANDOM_FILE_CHAR_LENGTH'], env_keys['TARGET_UTILITY'], execution_id)
        runner = ProgramRunner()
        create_directory('tmp_cache/' + execution_id)
        for execution_idx in range(env_keys['FUZZER_ITERATION']):
            original_cwd = os.getcwd()
            os.chdir('tmp_cache/' + execution_id)
            # execution_result is a tuple of format (result, outcome, input_to_utility)
            execution_result = fuzzer.run(runner)
            add_test_to_report(execution_result, test_cases_list, execution_idx, env_keys['TARGET_UTILITY'])
            os.chdir(original_cwd)
            sys.stdout.flush()
    elif env_keys['FUZZER_TYPE'] == 'RANDOM':

        fuzzer = RandomFuzzer(env_keys['TARGET_UTILITY'], execution_id)
        runner = ProgramRunner()
        create_directory('tmp_cache/' + execution_id)
        for execution_idx in range(env_keys['FUZZER_ITERATION']):
            # execution_result is a tuple of format (result, outcome, input_to_utility)
            original_cwd = os.getcwd()
            os.chdir('tmp_cache/' + execution_id)
            execution_result = fuzzer.run(runner)
            add_test_to_report(execution_result, test_cases_list, execution_idx, env_keys['TARGET_UTILITY'])
            os.chdir(original_cwd)
            sys.stdout.flush()

    # Lets dump all the test cases into a Junit style report.
    save_report(test_cases=test_cases_list)

    time.sleep(1000)
    # This is added to stop the container, We added this step to get the results outside of the container.
    while True:
        try:
            line = sys.stdin.readline()
            if line == "":
                break
        except KeyboardInterrupt as e:
            print("Received a termination signal, program will exit shortly")
            break
        except Exception as e:  # This is written to make sure any unhandled error should not crash the program.
            print("Error: Some generic error : {0}".format(line), file=sys.stderr)
            break

    # return exit code 0 on successful termination
    sys.exit(0)


if __name__ == '__main__':
    main()
