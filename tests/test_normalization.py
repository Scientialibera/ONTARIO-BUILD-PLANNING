from services.ontario_builds import normalize_record
from services.toronto import normalize_solicitation


def test_ontario_normalization_parses_budget_and_coordinates():
    row = {
        "Category": "Health care", "Project": "Hospital expansion", "Estimated Total Budget ($)": "125,000,000",
        "Latitude": "43.65", "Longitude": "-79.38", "Status": "Planning", "Target Completion Date": "2030-01-01"
    }
    project = normalize_record(row)
    assert project["budget"] == 125_000_000
    assert project["latitude"] == 43.65
    assert project["longitude"] == -79.38


def test_toronto_solicitation_normalization():
    row = {"Document Number": "123", "RFx (Solicitation) Type": "RFP", "Solicitation Document Description": "Engineering services", "Division": "Transportation Services"}
    item = normalize_solicitation(row)
    assert item["document_number"] == "123"
    assert item["division"] == "Transportation Services"
