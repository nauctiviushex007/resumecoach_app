from backend.analysis import analyze, new_numbers

RESUME = "Jane jane@x.com +1 555 123 4567\n- Responsible for building APIs in Python\n- Led a team of 4 to cut deploy time by 30% using Docker\n- Wrote tests"
JOB = "We need a Python developer with Docker, AWS and SQL. Python APIs, Docker pipelines, AWS deployments."


def test_match():
    a = analyze(RESUME, JOB)
    assert "python" in a["matched"] and "aws" in a["missing"]


def test_invented_number_flagged():
    assert new_numbers("Cut time", "Cut time by 45%") == ["45%"]
