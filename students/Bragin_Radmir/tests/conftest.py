import pytest

@pytest.fixture
def valid_int_value():
    return "42"

@pytest.fixture
def invalid_int_value():
    return "abc"