import pytest

from ragproject.prompts import load_prompt, latest_version


def test_load_prompt_v1_and_v2_exist():
    v1 = load_prompt("answer", "v1")
    v2 = load_prompt("answer", "v2")
    assert "{context}" in v1 and "{question}" in v1
    assert "{context}" in v2 and "{question}" in v2
    assert v1 != v2


def test_load_prompt_missing_raises_with_available_versions_listed():
    with pytest.raises(FileNotFoundError) as exc_info:
        load_prompt("answer", "v99")
    assert "v1" in str(exc_info.value) or "answer_v1.md" in str(exc_info.value)


def test_latest_version_returns_v2():
    assert latest_version("answer") == "v2"
