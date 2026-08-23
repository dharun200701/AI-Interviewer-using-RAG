import unittest
from unittest.mock import patch

from interviewer_agent import evaluate_answer


class InterviewerAgentTests(unittest.TestCase):
    @patch("interviewer_agent.evaluate_with_llama", return_value="8/10 - Good answer.")
    def test_evaluate_answer_returns_plain_string(self, mock_eval):
        result = evaluate_answer("Why do you want to work here?", "I want to grow.")
        self.assertEqual(result, "8/10 - Good answer.")
        self.assertNotIsInstance(result, dict)


if __name__ == "__main__":
    unittest.main()
