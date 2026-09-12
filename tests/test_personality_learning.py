from core.personality import FeedbackOutcome, LearningSignal
from core.personality_store import load_learning_signals, save_learning_signals


def test_correction_round_trips_as_structured_learning_signal(tmp_path) -> None:
    path = tmp_path / "personality_learning.json"
    signal = LearningSignal(
        original_input="draft a reply",
        candidate="generic answer",
        outcome=FeedbackOutcome.CORRECTED,
        correction="shorter reply",
        reason="too scripted",
        inferred_lesson="prefer one natural sentence in this context",
    )

    save_learning_signals([signal], path=path)
    loaded = load_learning_signals(path=path)

    assert loaded == [signal]
    assert loaded[0].outcome is FeedbackOutcome.CORRECTED
