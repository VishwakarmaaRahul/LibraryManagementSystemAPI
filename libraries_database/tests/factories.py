import factory
from factory.django import DjangoModelFactory
from datetime import date, timedelta
from faker import Faker
from libraries_database.models import Library, Author, Category, Book, Member, Borrowing

fake = Faker()

# -------------------------
# Library Factory
# -------------------------
class LibraryFactory(DjangoModelFactory):
    class Meta:
        model = Library

    library_name = factory.Faker("company")          # instead of campus_location
    campus_location = factory.Faker("city")         # valid Faker provider
    contact_email = factory.Faker("email")          # valid Faker provider
    phone_number = factory.Sequence(lambda n: f"100000000{n}")


# -------------------------
# Author Factory
# -------------------------
class AuthorFactory(DjangoModelFactory):
    class Meta:
        model = Author

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    birth_date = factory.Faker("date_of_birth")
    nationality = factory.Faker("country")
    biography = factory.Faker("paragraph")


# -------------------------
# Category Factory
# -------------------------
class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    category = factory.Faker("word")
    descriptions = factory.Faker("paragraph")


# -------------------------
# Member Factory
# -------------------------
class MemberFactory(DjangoModelFactory):
    class Meta:
        model = Member

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    contact_email = factory.Faker("email")          # fixed
    phone_number = factory.Sequence(lambda n: f"100000000{n}")
    member_type = Member.MemberType.STUDENT


# -------------------------
# Book Factory
# -------------------------
class BookFactory(DjangoModelFactory):
    class Meta:
        model = Book

    title = factory.Faker("sentence", nb_words=4)
    isbn = factory.Faker("isbn13")
    publication_date = factory.Faker("date")
    total_copies = factory.Faker("random_int", min=1, max=10)
    available_copies = factory.Faker("random_int", min=1, max=10)
    library = factory.SubFactory(LibraryFactory)

    @factory.post_generation
    def authors(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for author in extracted:
                self.authors.add(author)
        else:
            self.authors.add(AuthorFactory())

    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for category in extracted:
                self.categories.add(category)
        else:
            self.categories.add(CategoryFactory())


# -------------------------
# Borrowing Factory
# -------------------------
class BorrowingFactory(DjangoModelFactory):
    class Meta:
        model = Borrowing

    member = factory.SubFactory(MemberFactory)
    book = factory.SubFactory(BookFactory)
    borrow_date = factory.Faker("date_this_year")
    due_date = factory.Faker("future_date", end_date="+14d")
    return_date = None
    late_fee = 0