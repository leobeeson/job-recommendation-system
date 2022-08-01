import pytest

from recommender import Recommender


@pytest.fixture(scope='module', autouse=True)
def activities_dto():
    recommender = Recommender("dataset/activities.jsonl")
    return recommender


# Test no redirects:
test_data_no_redirects = [
    (3, 0, 1),
    (5, 0, 1),
    (1, 0, 1)
]
@pytest.mark.parametrize("impressions, redirects, expected_score", test_data_no_redirects)
def test_any_impressions_no_redirects_returns_one(activities_dto, impressions, redirects, expected_score) -> None:
    implicit_score = Recommender.calculate_implicit_score(impressions, redirects)
    assert implicit_score == expected_score


# Test 1 redirect:
test_data_no_redirects = [
    (3, 1, 3),
    (5, 1, 3),
    (1, 1, 3)
]
@pytest.mark.parametrize("impressions, redirects, expected_score", test_data_no_redirects)
def test_multiple_impressions_one_redirects_returns_three(activities_dto, impressions, redirects, expected_score) -> None:
    implicit_score = Recommender.calculate_implicit_score(impressions, redirects)
    assert implicit_score == expected_score

# Test 2 redirects:
test_data_no_redirects = [
    (3, 2, 6),
    (5, 2, 6),
    (8, 2, 6)
]
@pytest.mark.parametrize("impressions, redirects, expected_score", test_data_no_redirects)
def test_multiple_impressions_two_redirects_returns_six(activities_dto, impressions, redirects, expected_score) -> None:
    implicit_score = Recommender.calculate_implicit_score(impressions, redirects)
    assert implicit_score == expected_score

# Test impressions-to-redirects efficiency:
test_data_no_redirects = [
    (1, 3, 7),
    (2, 3, 8),
    (3, 3, 9),
    (4, 3, 9),
    (5, 3, 9),
]
@pytest.mark.parametrize("impressions, redirects, expected_score", test_data_no_redirects)
def test_fewer_and_greater_impressions_than_redirects_returns_plateauing_score(activities_dto, impressions, redirects, expected_score) -> None:
    implicit_score = Recommender.calculate_implicit_score(impressions, redirects)
    assert implicit_score == expected_score

# Test excessive impressions clipping:
test_data_no_redirects = [
    (11, 0, 1),
    (100, 1, 3),
    (1000, 2, 6)
]
@pytest.mark.parametrize("impressions, redirects, expected_score", test_data_no_redirects)
def test_excessive_impressions_are_clipped(activities_dto, impressions, redirects, expected_score) -> None:
    implicit_score = Recommender.calculate_implicit_score(impressions, redirects)
    assert implicit_score == expected_score

# Test excessive redirects clipping:
test_data_no_redirects = [
    (1, 11, 21),
    (3, 111, 23),
    (6, 1000, 26)
]
@pytest.mark.parametrize("impressions, redirects, expected_score", test_data_no_redirects)
def test_excessive_redirects_are_clipped(activities_dto, impressions, redirects, expected_score) -> None:
    implicit_score = Recommender.calculate_implicit_score(impressions, redirects)
    assert implicit_score == expected_score
