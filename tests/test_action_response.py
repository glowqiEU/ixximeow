import unittest

from core.action_response import ActionResponse


class TestActionResponse(unittest.TestCase):
    def test_response_preserves_success_summary_and_output(self):
        response = ActionResponse(
            success=True,
            summary="state inspected",
            output={"active": False},
        )

        self.assertTrue(response.success)
        self.assertEqual(response.summary, "state inspected")
        self.assertEqual(response.output, {"active": False})

    def test_empty_summary_fails(self):
        with self.assertRaises(ValueError):
            ActionResponse(success=True, summary="")

    def test_non_boolean_success_fails(self):
        with self.assertRaises(ValueError):
            ActionResponse(success="yes", summary="done")


if __name__ == "__main__":
    unittest.main()
