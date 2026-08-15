from datetime import date
from domain.scoring import planning_complexity


def test_large_planning_project_with_near_term_date_scores_high():
    project = {
        "status": "Planning",
        "category": "Transit",
        "budget": 800_000_000,
        "target_completion": "2026-12-01",
        "provincial_funding": "Yes",
        "federal_funding": "Yes",
        "municipal_funding": "Yes",
        "latitude": 43.65,
        "longitude": -79.38,
    }
    result = planning_complexity(project, today=date(2026, 8, 15))
    assert result["score"] >= 70
    assert result["band"] in {"high", "very high"}


def test_completed_small_project_is_low_complexity():
    project = {"status": "Complete", "category": "Recreation", "budget": 2_000_000, "target_completion": "2025-01-01", "latitude": 44, "longitude": -80}
    result = planning_complexity(project, today=date(2026, 8, 15))
    assert result["score"] < 30
