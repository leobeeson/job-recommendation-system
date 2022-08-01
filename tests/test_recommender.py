import pytest

from recommender import Recommender


@pytest.fixture(scope='module', autouse=True)
def activities_dto():
    recommender = Recommender("dataset/activities.jsonl")
    recommender.add_implicit_scores()
    return recommender


# Test no redirects:
test_data_no_redirects = [
    (3, 0, 1),
    (5, 0, 1),
    (1, 0, 1)
]
@pytest.mark.parametrize("impressions, redirects, expected_score", test_data_no_redirects)
def test_any_impressions_no_redirects_returns_one(impressions, redirects, expected_score) -> None:
    implicit_score = Recommender.calculate_implicit_score(impressions, redirects)
    assert implicit_score == expected_score


# Test 1 redirect:
test_data_one_redirect = [
    (3, 1, 3),
    (5, 1, 3),
    (1, 1, 3)
]
@pytest.mark.parametrize("impressions, redirects, expected_score", test_data_one_redirect)
def test_multiple_impressions_one_redirects_returns_three(impressions, redirects, expected_score) -> None:
    implicit_score = Recommender.calculate_implicit_score(impressions, redirects)
    assert implicit_score == expected_score

# Test 2 redirects:
test_data_two_redirects = [
    (3, 2, 6),
    (5, 2, 6),
    (8, 2, 6)
]
@pytest.mark.parametrize("impressions, redirects, expected_score", test_data_two_redirects)
def test_multiple_impressions_two_redirects_returns_six(impressions, redirects, expected_score) -> None:
    implicit_score = Recommender.calculate_implicit_score(impressions, redirects)
    assert implicit_score == expected_score

# Test impressions-to-redirects efficiency:
test_data_increasing_impressions = [
    (1, 3, 7),
    (2, 3, 8),
    (3, 3, 9),
    (4, 3, 9),
    (5, 3, 9),
]
@pytest.mark.parametrize("impressions, redirects, expected_score", test_data_increasing_impressions)
def test_fewer_and_greater_impressions_than_redirects_returns_plateauing_score(impressions, redirects, expected_score) -> None:
    implicit_score = Recommender.calculate_implicit_score(impressions, redirects)
    assert implicit_score == expected_score

# Test excessive impressions clipping:
test_data_excessive_impressions = [
    (11, 0, 1),
    (100, 1, 3),
    (1000, 2, 6)
]
@pytest.mark.parametrize("impressions, redirects, expected_score", test_data_excessive_impressions)
def test_excessive_impressions_are_clipped(impressions, redirects, expected_score) -> None:
    implicit_score = Recommender.calculate_implicit_score(impressions, redirects)
    assert implicit_score == expected_score

# Test excessive redirects clipping:
test_data_excessive_redirects = [
    (1, 11, 21),
    (3, 111, 23),
    (6, 1000, 26)
]
@pytest.mark.parametrize("impressions, redirects, expected_score", test_data_excessive_redirects)
def test_excessive_redirects_are_clipped(impressions, redirects, expected_score) -> None:
    implicit_score = Recommender.calculate_implicit_score(impressions, redirects)
    assert implicit_score == expected_score

# Test implicit scores setting:
test_data_implicit_scores_set = [
    (65794, 20116, 1),
    (65794, 15675, 1),
    (65794, 14884, 6),
    (65794, 16588, 3),
    (31004, 20515, 1),
    (31004, 20022, 1),
    (31004, 16718, 3),
    (31004, 25427, 3)
    ]
@pytest.mark.parametrize("user_id, job_id, expected_score", test_data_implicit_scores_set)
def test_implicit_scores_are_retrieved_from_activities_data_properly(activities_dto, user_id, job_id, expected_score) -> None:
    implicit_score = activities_dto.activities[user_id][job_id].get(Recommender.implicit_score_key)
    assert implicit_score == expected_score
