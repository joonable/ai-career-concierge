from agent.prompts.memory_summary import summarize_recent_dislikes


def test_summarize_recent_dislikes_deduplicates_and_preserves_order():
    summary = summarize_recent_dislikes(
        ["salary too low", "contract-only", "salary too low", "pure frontend"]
    )

    assert "salary too low" in summary
    assert summary.count("salary too low") == 1
    assert "contract-only" in summary
    assert "pure frontend" in summary
