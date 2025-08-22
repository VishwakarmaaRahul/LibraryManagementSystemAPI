import pytest
from rest_framework.test import APIClient

from .factories import LibraryFactory, AuthorFactory, CategoryFactory, BookFactory, MemberFactory

# -------------------------
# API Client Fixture
# -------------------------
@pytest.fixture
def api_client():
    return APIClient()


# -------------------------
# Library Fixture
# -------------------------
@pytest.fixture
def library():
    return LibraryFactory()


# -------------------------
# Book Fixture
# -------------------------
@pytest.fixture
def book(library, author, category):
    return BookFactory(
        library=library,
        authors=[author],
        categories=[category]
    )



# -------------------------
# Member Fixture
# -------------------------
@pytest.fixture
def member():
    return MemberFactory()


# -------------------------
# Author Fixture
# -------------------------
@pytest.fixture
def author():
    return AuthorFactory()


# -------------------------
# Category Fixture
# -------------------------
@pytest.fixture
def category():
    return CategoryFactory()
