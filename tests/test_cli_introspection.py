import io
import json
import unittest
from contextlib import redirect_stdout

import inkctl


class CliIntrospectionTests(unittest.TestCase):
    def test_capabilities_json_lists_known_commands(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = inkctl.main(["capabilities", "--json"])

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        command_names = {command["name"] for command in payload["commands"]}
        self.assertIn("get-selection", command_names)
        self.assertIn("select-elements", command_names)
        self.assertIn("capabilities", command_names)

    def test_command_help_json_describes_arguments(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = inkctl.main(["get-selection", "--help", "--json"])

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["name"], "get-selection")
        self.assertIn("inkctl get-selection", payload["usage"])
        argument_names = {argument["name"] for argument in payload["arguments"]}
        self.assertIn("file", argument_names)

    def test_root_help_json_returns_capabilities_payload(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = inkctl.main(["--help", "--json"])

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["program"], "inkctl")
        self.assertIn("commands", payload)


if __name__ == "__main__":
    unittest.main()
