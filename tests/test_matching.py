from domain.matching import opportunity_matches, text_similarity


def test_related_watermain_text_scores_above_unrelated_text():
    related = text_similarity("Bloor Street watermain replacement", "Watermain replacement on Bloor Street and valve work")
    unrelated = text_similarity("Bloor Street watermain replacement", "Supply of office furniture")
    assert related > unrelated
    assert related > 0.4


def test_matcher_returns_candidate():
    pipeline = [{"project": "Bloor Street watermain replacement", "description": "Replace trunk watermain", "division": "Toronto Water"}]
    solicitations = [{"document_number": "DOC-1", "description": "Bloor Street trunk watermain replacement", "division": "Toronto Water", "category": "Construction Services"}]
    result = opportunity_matches(pipeline, solicitations)
    assert result[0]["matches"]
    assert result[0]["matches"][0]["solicitation"]["document_number"] == "DOC-1"
