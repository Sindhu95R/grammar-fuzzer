from utils.unix_utils import execute_command
from utils.exit_codes import codes


class ProgramRunner():
    # Test outcomes
    PASS = "PASS"
    FAIL = "FAIL"
    UNRESOLVED = "UNRESOLVED"

    def __init__(self, program=None):
        """Initialize.  `program` is a program spec as passed to `subprocess.run()`"""
        self.program = program

    def run(self, inp=""):
        """Run the program with `inp` as input.  Return test outcome based on result of `subprocess.run()`."""
        result = execute_command(inp)
        # print(result)

        if result["exit code"] == codes["OK"]:
            outcome = self.PASS
            # print("Status Code: OK")
        elif result["exit code"] == codes["illegal option"]:
            # outcome = self.FAIL
            outcome = self.PASS
            # print("Status Code: illegal option")
        elif result["exit code"] == codes["command not found"]:
            # outcome = self.FAIL
            outcome = self.PASS
            # print("Status Code: command not found")
        elif result["exit code"] == codes["Out of memory"]:
            outcome = self.FAIL
            # print("Status Code: Out of memory")
        elif result["exit code"] == codes["Segmentation Fault"]:
            outcome = self.FAIL
            # print("Status Code: Segmentation Fault {0}".format(inp))
        elif result["exit code"] < 0:
            outcome = self.FAIL
            # outcome = self.PASS
        elif result["exit code"] == codes["Fuzzer Exception"]:
            outcome = self.FAIL
        else:
            outcome = self.UNRESOLVED

        return result, outcome, inp