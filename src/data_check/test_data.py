import pandas as pd
import numpy as np
import scipy.stats


def test_column_names(data):

    expected_colums = [
        "id",
        "name",
        "host_id",
        "host_name",
        "neighbourhood_group",
        "neighbourhood",
        "latitude",
        "longitude",
        "room_type",
        "price",
        "minimum_nights",
        "number_of_reviews",
        "last_review",
        "reviews_per_month",
        "calculated_host_listings_count",
        "availability_365",
    ]

    these_columns = data.columns.values

    # This also enforces the same order
    assert list(expected_colums) == list(these_columns)


def test_neighborhood_names(data):

    known_names = ["Bronx", "Brooklyn", "Manhattan", "Queens", "Staten Island"]

    neigh = set(data['neighbourhood_group'].unique())

    # Unordered check
    assert set(known_names) == set(neigh)


def test_proper_boundaries(data: pd.DataFrame):
    """
    Test proper longitude and latitude boundaries for properties in and around NYC
    """
    idx = data['longitude'].between(-74.25, -73.50) & data['latitude'].between(40.5, 41.2)

    assert np.sum(~idx) == 0




# def test_similar_neigh_distrib(data: pd.DataFrame, ref_data: pd.DataFrame, kl_threshold: float):
#     """
#     Apply a threshold on the KL divergence to detect if the distribution of the new data is
#     significantly different than that of the reference dataset.

#     This test is robust against cases where a category exists in one dataset but not the other.
#     """
#     # 1. Get the value counts for the 'neighbourhood_group' column in both dataframes
#     dist1 = data['neighbourhood_group'].value_counts().sort_index()
#     dist2 = ref_data['neighbourhood_group'].value_counts().sort_index()

#     # 2. Get all unique categories from both distributions combined
#     all_categories = sorted(list(set(dist1.index) | set(dist2.index)))

#     # 3. Reindex both distributions to have the same categories, filling missing ones with 0
#     dist1 = dist1.reindex(all_categories, fill_value=0)
#     dist2 = dist2.reindex(all_categories, fill_value=0)

#     # 4. Add a small epsilon to avoid division by zero or log(0) issues in entropy calculation
#     # This prevents the KL divergence from becoming infinity if a category exists in the new
#     # data but not in the reference data.
#     dist1 = dist1 + 1e-9
#     dist2 = dist2 + 1e-9

#     # 5. Calculate the KL divergence and assert it's below the threshold
#     kl_divergence = scipy.stats.entropy(dist1, dist2, base=2)

#     assert kl_divergence < kl_threshold, (
#         f"KL divergence of {kl_divergence:.4f} is above the threshold of {kl_threshold}. "
#         f"The distribution of neighbourhood_group has drifted."
#     )



########################################################
# Implement here test_row_count and test_price_range   #
########################################################
def test_row_count(data):
    assert 15000 < data.shape[0] < 1000000


import pandas as pd
import pytest

# This is the function you were asked to write
def test_price_range(data: pd.DataFrame, min_price: float, max_price: float):
    """
    Checks if all values in the 'price' column of a DataFrame are between
    min_price and max_price, inclusive.
    """
    is_in_range = data["price"].between(min_price, max_price).all()
    assert is_in_range, f"Found prices outside the [{min_price}, {max_price}] range."


# Now, we write helper tests to call this function with different data
# to see if it behaves as expected.

def test_price_range_passes():
    """Test with data that is entirely within the valid range."""
    min_p, max_p = 100, 500
    df = pd.DataFrame({
        "price": [101, 250, 499]
    })
    # This should run without raising an error
    test_price_range(df, min_p, max_p)

def test_price_range_boundaries_inclusive():
    """Test with data exactly on the boundaries, which should pass."""
    min_p, max_p = 100, 500
    df = pd.DataFrame({
        "price": [100, 250, 500]
    })
    # This should also pass because .between() is inclusive by default
    test_price_range(df, min_p, max_p)

def test_price_range_fails_low():
    """Test with data containing a price below the minimum."""
    min_p, max_p = 100, 500
    df = pd.DataFrame({
        "price": [101, 99, 499]  # 99 is out of range
    })
    # We expect this to fail, so we check that it raises an AssertionError
    with pytest.raises(AssertionError):
        test_price_range(df, min_p, max_p)

def test_price_range_fails_high():
    """Test with data containing a price above the maximum."""
    min_p, max_p = 100, 500
    df = pd.DataFrame({
        "price": [101, 501, 499]  # 501 is out of range
    })
    # We expect this to fail as well
    with pytest.raises(AssertionError):
        test_price_range(df, min_p, max_p)