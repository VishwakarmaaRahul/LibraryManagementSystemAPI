import django_filters
from django.db.models import Q
from .models import Library, Book, Author, Category, Member, Borrowing, Review


class LibraryFilter(django_filters.FilterSet):
    library_name = django_filters.CharFilter(field_name='library_name', lookup_expr='icontains')
    campus_location = django_filters.CharFilter(method='filter_campus_location')
    contact_email = django_filters.CharFilter(field_name='contact_email', lookup_expr='icontains')
    phone_number = django_filters.CharFilter(field_name='phone_number', lookup_expr='exact')
    created_at = django_filters.DateFromToRangeFilter(field_name='created_at')
    updated_at = django_filters.DateFromToRangeFilter(field_name='updated_at')

    def filter_campus_location(self, queryset, name, value):
        # Support partial or exact case-insensitive campus location filtering
        return queryset.filter(Q(campus_location__icontains=value) | Q(campus_location__iexact=value))

    class Meta:
        model = Library
        fields = ['library_name', 'campus_location', 'contact_email', 'phone_number', 'created_at', 'updated_at']



class BookFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(method='filter_title')
    isbn = django_filters.CharFilter(field_name='isbn', lookup_expr='exact')
    publication_date = django_filters.DateFromToRangeFilter(field_name='publication_date')
    library = django_filters.NumberFilter(field_name='library', lookup_expr='exact')
    available_copies__gte = django_filters.NumberFilter(field_name='available_copies', lookup_expr='gte')
    available_copies__lte = django_filters.NumberFilter(field_name='available_copies', lookup_expr='lte')
    total_copies__gte = django_filters.NumberFilter(field_name='total_copies', lookup_expr='gte')
    total_copies__lte = django_filters.NumberFilter(field_name='total_copies', lookup_expr='lte')

    authors = django_filters.ModelMultipleChoiceFilter(
        method='filter_authors',
        queryset=Author.objects.all(),
        conjoined=False,
    )

    categories = django_filters.ModelMultipleChoiceFilter(
        method='filter_categories',
        queryset=Category.objects.all(),
        conjoined=False,
    )

    def filter_title(self, queryset, name, value):
        return queryset.filter(title__icontains=value)

    def filter_authors(self, queryset, name, value):
        if not value:
            return queryset
        author_ids = [author.author_id for author in value]
        return queryset.filter(bookauthor__author_id__in=author_ids).distinct()

    def filter_categories(self, queryset, name, value):
        if not value:
            return queryset
        category_ids = [category.category_id for category in value]
        return queryset.filter(bookcategory__category_id__in=category_ids).distinct()

    class Meta:
        model = Book
        fields = [
            'title', 'isbn', 'publication_date', 'library',
            'available_copies__gte', 'available_copies__lte',
            'total_copies__gte', 'total_copies__lte',
            'authors',  # Add these so they are recognized
            'categories',
        ]


class AuthorFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(method='filter_first_name')
    last_name = django_filters.CharFilter(method='filter_last_name')
    birth_date = django_filters.DateFromToRangeFilter(field_name='birth_date')
    nationality = django_filters.CharFilter(field_name='nationality', lookup_expr='icontains')

    def filter_first_name(self, queryset, name, value):
        return queryset.filter(first_name__icontains=value)

    def filter_last_name(self, queryset, name, value):
        return queryset.filter(last_name__icontains=value)

    class Meta:
        model = Author
        fields = ['first_name', 'last_name', 'birth_date', 'nationality']


class CategoryFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(method='filter_category')
    descriptions = django_filters.CharFilter(field_name='descriptions', lookup_expr='icontains')

    def filter_category(self, queryset, name, value):
        return queryset.filter(category__icontains=value)

    class Meta:
        model = Category
        fields = ['category', 'descriptions']


class MemberFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(method='filter_first_name')
    last_name = django_filters.CharFilter(method='filter_last_name')
    contact_email = django_filters.CharFilter(field_name='contact_email', lookup_expr='icontains')
    phone_number = django_filters.CharFilter(field_name='phone_number', lookup_expr='icontains')
    member_type = django_filters.CharFilter(field_name='member_type', lookup_expr='exact')

    def filter_first_name(self, queryset, name, value):
        return queryset.filter(first_name__icontains=value)

    def filter_last_name(self, queryset, name, value):
        return queryset.filter(last_name__icontains=value)

    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'contact_email', 'phone_number', 'member_type']


class BorrowingFilter(django_filters.FilterSet):
    member = django_filters.NumberFilter(field_name='member', lookup_expr='exact')
    book = django_filters.NumberFilter(field_name='book', lookup_expr='exact')
    borrow_date = django_filters.DateFromToRangeFilter(field_name='borrow_date')
    due_date = django_filters.DateFromToRangeFilter(field_name='due_date')
    return_date = django_filters.DateFilter(field_name='return_date')
    return_date_isnull = django_filters.BooleanFilter(field_name='return_date', lookup_expr='isnull')
    late_fee__gte = django_filters.NumberFilter(field_name='late_fee', lookup_expr='gte')
    late_fee__lte = django_filters.NumberFilter(field_name='late_fee', lookup_expr='lte')

    class Meta:
        model = Borrowing
        fields = [
            'member', 'book', 'borrow_date', 'due_date',
            'return_date', 'return_date_isnull', 'late_fee__gte', 'late_fee__lte'
        ]


class ReviewFilter(django_filters.FilterSet):
    member = django_filters.NumberFilter(field_name='member', lookup_expr='exact')
    book = django_filters.NumberFilter(field_name='book', lookup_expr='exact')
    rating__exact = django_filters.NumberFilter(field_name='rating', lookup_expr='exact')
    rating__gte = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    rating__lte = django_filters.NumberFilter(field_name='rating', lookup_expr='lte')
    review_date = django_filters.DateFromToRangeFilter(field_name='review_date')

    class Meta:
        model = Review
        fields = [
            'member', 'book',
            'rating__exact', 'rating__gte', 'rating__lte',
            'review_date'
        ]
