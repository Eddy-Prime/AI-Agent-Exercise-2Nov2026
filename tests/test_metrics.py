from judge import abstains, must_contain_pass, rule_pass

ANSWERABLE = {"answerable": True, "must_contain": ["ptrace_scope"]}
UNANSWERABLE = {"answerable": False, "must_contain": []}


def test_must_contain_needs_all_facts():
    assert must_contain_pass("Use /proc/sys/kernel/yama/ptrace_scope", ["ptrace_scope"])
    assert not must_contain_pass("Use sudo", ["ptrace_scope"])
    assert not must_contain_pass("It is memoryview", ["memoryview", "queue"])


def test_abstain_detection():
    assert abstains("That information is not in the documents.")
    assert abstains("The passages don’t specify this, and it is not mentioned.")
    assert not abstains("It uses 32 bytes.")


def test_rule_pass_for_both_question_types():
    assert rule_pass(ANSWERABLE, "write 0 to ptrace_scope")
    assert not rule_pass(ANSWERABLE, "I do not know")
    assert rule_pass(UNANSWERABLE, "This is not mentioned in the documents.")
    assert not rule_pass(UNANSWERABLE, "It is 4.8.")


def test_percent_with_space_and_special_hyphen_match():
    assert must_contain_pass("It saves about 8 % of time", ["8%"])
    assert must_contain_pass("a free\u2011threaded build", ["free-threaded"])


def test_more_abstain_wordings():
    assert abstains("The passages do not contain this information.")
    assert abstains("That detail is not present.")
    assert abstains("There is no mention of it.")
