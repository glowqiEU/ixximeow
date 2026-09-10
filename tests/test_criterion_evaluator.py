import unittest

from core.evidence import Evidence
from core.objective import ObjectiveCriterion
from core.criterion_evaluator import evaluate_criterion


class TestCriterionEvaluator(unittest.TestCase):
    def test_exists_requires_verified_evidence(self):
        criterion = ObjectiveCriterion(name="post exists", kind="exists")
        evidence = Evidence(
            result_id="result-1",
            execution_id="execution-1",
            kind="external_observation",
            content="post appears visible",
            verified=True,
        )

        self.assertTrue(evaluate_criterion(criterion, [evidence]))

    def test_unverified_evidence_is_not_proof(self):
        criterion = ObjectiveCriterion(name="post exists", kind="exists")
        evidence = Evidence(
            result_id="result-1",
            execution_id="execution-1",
            kind="external_observation",
            content="post appears visible",
            verified=False,
        )

        self.assertIsNone(evaluate_criterion(criterion, [evidence]))

    def test_contains_matches_verified_evidence(self):
        criterion = ObjectiveCriterion(
            name="contains published",
            kind="contains",
            expected="published",
        )
        evidence = Evidence(
            result_id="result-1",
            execution_id="execution-1",
            kind="execution_log",
            content="post was published successfully",
            verified=True,
        )

        self.assertTrue(evaluate_criterion(criterion, [evidence]))

    def test_equals_requires_exact_verified_content(self):
        criterion = ObjectiveCriterion(
            name="status is published",
            kind="equals",
            expected="published",
        )
        evidence = Evidence(
            result_id="result-1",
            execution_id="execution-1",
            kind="status",
            content="published",
            verified=True,
        )

        self.assertTrue(evaluate_criterion(criterion, [evidence]))

    def test_boolean_requires_explicit_boolean_evidence(self):
        criterion = ObjectiveCriterion(
            name="post is visible",
            kind="boolean",
            expected=True,
        )
        evidence = Evidence(
            result_id="result-1",
            execution_id="execution-1",
            kind="boolean",
            content="true",
            verified=True,
        )

        self.assertTrue(evaluate_criterion(criterion, [evidence]))

    def test_boolean_false_is_explicit_failure(self):
        criterion = ObjectiveCriterion(
            name="post is visible",
            kind="boolean",
            expected=True,
        )
        evidence = Evidence(
            result_id="result-1",
            execution_id="execution-1",
            kind="boolean",
            content="false",
            verified=True,
        )

        self.assertFalse(evaluate_criterion(criterion, [evidence]))

    def test_non_matching_evidence_is_unknown(self):
        criterion = ObjectiveCriterion(
            name="status is published",
            kind="equals",
            expected="published",
        )
        evidence = Evidence(
            result_id="result-1",
            execution_id="execution-1",
            kind="status",
            content="draft",
            verified=True,
        )

        self.assertIsNone(evaluate_criterion(criterion, [evidence]))

    def test_empty_evidence_is_unknown(self):
        criterion = ObjectiveCriterion(name="post exists", kind="exists")

        self.assertIsNone(evaluate_criterion(criterion, []))


if __name__ == "__main__":
    unittest.main()
