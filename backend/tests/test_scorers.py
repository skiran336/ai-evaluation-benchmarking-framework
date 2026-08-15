from app.scorers.deterministic import exact_match, required_terms_score, token_f1


def test_exact_match_ignores_case_and_punctuation():
    assert exact_match("Paris!", "paris") == 1.0


def test_token_f1_rewards_overlap():
    assert token_f1("Kafka uses partitions", "Kafka partitions enable scale") > 0.4


def test_required_terms_score():
    assert required_terms_score("Use retries and idempotency", ["retries", "idempotency"]) == 1.0
