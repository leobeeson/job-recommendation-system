import pytest

from recommender import Recommender


@pytest.fixture(scope='module', autouse=True)
def activities_dto():
    recommender = Recommender("tests/test_data/test_activities.jsonl")
    recommender.build_sparse_matrix()
    return recommender

@pytest.fixture()
def expected_user_job_triples():
    user_job_triples_dummy_data = [
        {'user_id': 65794, 'job_id': 16588, 'implicit_score': 3},
        {'user_id': 31004, 'job_id': 20515, 'implicit_score': 1}
    ]
    return user_job_triples_dummy_data
    
@pytest.fixture()
def expected_unique_entities():
    entity_indices = {
        "unique_users": [31004, 65794],
        "unique_jobs": [16588, 20515]
    }
    return entity_indices


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
def test_implicit_scores_are_retrieved_from_activities_data_properly(activities_dto, expected_user_job_triples) -> None:
    user_job_implicit_scores = activities_dto.user_job_implicit_scores
    assert user_job_implicit_scores == expected_user_job_triples

# Test implicit scores setting:
def test_unique_entities_are_identified_properly(activities_dto, expected_unique_entities) -> None:
    entity_indices = activities_dto.entity_indices
    assert entity_indices == expected_unique_entities

# Test csr matrix has correct dimensions:
def test_csr_matrix_has_correct_dimensions(activities_dto, expected_unique_entities) -> None:
    rows_dim = len(expected_unique_entities["unique_users"])
    columns_dim = len(expected_unique_entities["unique_jobs"])
    expected_matrix_shape = (rows_dim, columns_dim)
    csr_matrix_shape = activities_dto.matrix_csr.shape
    assert csr_matrix_shape == expected_matrix_shape
