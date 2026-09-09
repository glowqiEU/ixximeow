import unittest

from core.criterion_evaluator import evaluate_criterion, evaluate_criteria
from core.evidence import Evidence
from core.objective import ObjectiveCriterion


class TestCriterionEvaluator(unittest.TestCase):
    def evidence(self, claim, value, verified=True, id="evidence-1"):
        return Evidence(
            result_id="result-1",
            execution_id="execution-1",
            kind="external_observation",
            claim=claim,
            value=value,
            content=f"{claim}: {value}",
            verified=verified,
            id=id,
        )

    def test_equals_passes_with_matching_verified_value(self):
        criterion = ObjectiveCriterion(
            claim="post_visible",
            kind="equals",
            expected=True,
        )
        evaluation = evaluate_criterion(
            criterion,
            [self.evidence("post_visible", True)],
        )

        self.assertEqual(evaluation.status, "passed")
        self.assertEqual(evaluation.evidence_ids, ["evidence-1"])

    def test_boolean_fails_with_wrong_verified_value(self):
        criterion = ObjectiveCriterion(
            claim="post_visible",
            kind="boolean",
            expected=True,
        )
        evaluation = evaluate_criterion(
            criterion,
            [self.evidence("post_visible", False)],
        )

        self.assertEqual(evaluation.status, "failed")

    def test_missing_unverified_evidence_cannot_prove_criterion(self):
        criterion = ObjectiveCriterion(
            claim="post_visible",
            kind="boolean",
            expected=True,
        )
        evaluation = evaluate_criterion(
            criterion,
            [self.evidence("post_visible", True, verified=False)],
        )

        self.assertEqual(evaluation.status, "missing")
        self.assertEqual(evaluation.evidence_ids, [])

    def test_conflicting_verified_values_are_uncertain(self):
        criterion = ObjectiveCriterion(
            claim="post_visible",
            kind="boolean",
            expected=True,
        )
        evaluation = evaluate_criterion(
            criterion,
            [
                self.evidence("post_visible", True, id="evidence-1"),
                self.evidence("post_visible", False, id="evidence-2"),
            ],
        )

        self.assertEqual(evaluation.status, "conflict")
        self.assertEqual(
            evaluation.evidence_ids,
            ["evidence-1", "evidence-2"],
        )

    def test_exists_passes_when_verified_claim_exists(self):
        criterion = ObjectiveCriterion(claim="published_at", kind="exists")
        evaluation = evaluate_criterion(
            criterion,
            [self.evidence("published_at", "2026-09-09T18:00:00Z")],
        )

        self.assertEqual(evaluation.status, "passed")

    def test_contains_supports_strings_and_lists(self):
        string_criterion = ObjectiveCriterion(
            claim="caption",
            kind="contains",
            expected="second look",
        )
        list_criterion = ObjectiveCriterion(
            claim="tags",
            kind="contains",
            expected="psychology",
        )

        self.assertEqual(
            evaluate_criterion(
                string_criterion,
                [self.evidence("caption", "a second look at behavior")],
            ).status,
            "passed",
        )
        self.assertEqual(
            evaluate_criterion(
                list_criterion,
                [self.evidence("tags", ["psychology", "x"])],
            ).status,
            "passed",
        )

    def test_only_matching_claims_are_considered(self):
        criterion = ObjectiveCriterion(
            claim="post_visible",
            kind="boolean",
            expected=True,
        )
        evaluation = evaluate_criterion(
            criterion,
            [
                self.evidence("post_visible", True, id="evidence-1"),
                self.evidence("post_id", "123", id="evidence-2"),
            ],
        )

        self.assertEqual(evaluation.status, "passed")
        self.assertEqual(evaluation.evidence_ids, ["evidence-1"])

    def test_all_criteria_are_evaluated_independently(self):
        criteria = [
            ObjectiveCriterion("post_visible", "boolean", True),
            ObjectiveCriterion("post_id", "equals", "123"),
        ]
        evaluations = evaluate_criteria(
            criteria,
            [
                self.evidence("post_visible", True, id="evidence-1"),
                self.evidence("post_id", "123", id="evidence-2"),
            ],
        )

        self.assertEqual([item.status for item in evaluations], ["passed", "passed"])


if __name__ == "__main__":
    unittest.main()
