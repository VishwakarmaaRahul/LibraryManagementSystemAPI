import pytest
from django.urls import reverse
from .factories import BookFactory, MemberFactory, BorrowingFactory, AuthorFactory, CategoryFactory, LibraryFactory


pytestmark = pytest.mark.django_db


# ------------------------------
# Library Tests
# ------------------------------
def test_list_libraries(client):
    LibraryFactory.create_batch(3)
    url = reverse("library-list")
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.data['results']) == 3


# ------------------------------
# Book Tests
# ------------------------------
def test_list_books(client):
    BookFactory.create_batch(2)
    url = reverse("book-list")
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.data['results']) == 2


def test_create_book(client):
    # create a library first
    library = LibraryFactory()

    # build a book with that library
    book_data = BookFactory.build(library=library)

    url = reverse("book-list")
    response = client.post(url, {
        "title": book_data.title,
        "isbn": book_data.isbn,
        "library": library.pk,  # pass a real library ID
        "total_copies": book_data.total_copies,
        "available_copies": book_data.available_copies,
        "authors": [AuthorFactory().author_id],
        "categories": [CategoryFactory().category_id],
    })

    assert response.status_code == 201




def test_book_availability_action(client):
    book = BookFactory(available_copies=3, total_copies=5)
    url = reverse("book-availability", args=[book.book_id])
    response = client.get(url)
    assert response.status_code == 200
    assert response.data["available_copies"] == 3
    assert response.data["total_copies"] == 5


def test_borrow_book(client):
    book = BookFactory(available_copies=1)
    member = MemberFactory()
    url = reverse("book-borrow-book")
    response = client.post(url, {
        "book_id": book.book_id,
        "member_id": member.member_id,
        "borrow_date": "2025-08-10",
        "due_date": "2025-08-24"
    })
    assert response.status_code == 200
    assert response.data["status"] == "Book borrowed successfully."


def test_return_book(client):
    borrowing = BorrowingFactory(return_date=None)
    url = reverse("book-return-book")
    response = client.post(url, {"borrowing_id": borrowing.borrowing_id})
    assert response.status_code == 200
    assert "late_fee" in response.data
    assert response.data["status"] == "Book returned."


# ------------------------------
# Author Tests
# ------------------------------
def test_list_authors(client):
    AuthorFactory.create_batch(4)
    url = reverse("author-list")
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 4


# ------------------------------
# Category Tests
# ------------------------------
def test_list_categories(client):
    CategoryFactory.create_batch(4)
    url = reverse("category-list")
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 4


# ------------------------------
# Member Tests
# ------------------------------
def test_list_members(client):
    MemberFactory.create_batch(4)
    url = reverse("member-list")
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 4


# ------------------------------
# Active Borrowings
# ------------------------------
def test_member_active_borrowings_action(client):
    member = MemberFactory()
    BorrowingFactory.create_batch(2, member=member, return_date=None)
    url = reverse("member-active-borrowings", args=[member.member_id])
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 2


# ------------------------------
# Borrowing History
# ------------------------------
def test_member_borrowing_history_view(client):
    member = MemberFactory()
    BorrowingFactory.create_batch(3, member=member)
    url = reverse("member-borrowing-history", args=[member.member_id])
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 3
