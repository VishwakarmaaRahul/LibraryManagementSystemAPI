# from .fields import PhoneNumberField
# from rest_framework import serializers
# from .models import *
# from drf_spectacular.utils import extend_schema_field
#
# class AuthorNestedSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Author
#         fields = ['author_id', 'first_name', 'last_name']
#
# class CategoryNestedSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = ['category_id', 'category']
#
#
# class LibrarySerializer(serializers.ModelSerializer):
#     contact_email = serializers.EmailField(required=True)
#     phone_number = PhoneNumberField(required=True)
#
#     class Meta:
#         model = Library
#         fields = '__all__'
#
#
#
# class BookSerializer(serializers.ModelSerializer):
#     authors = serializers.PrimaryKeyRelatedField(
#         queryset=Author.objects.all(), many=True, write_only=True, required=False
#     )
#     categories = serializers.PrimaryKeyRelatedField(
#         queryset=Category.objects.all(), many=True, write_only=True, required=False
#     )
#     authors_detail = AuthorNestedSerializer(many=True, read_only=True, source='authors')
#     categories_detail = CategoryNestedSerializer(many=True, read_only=True, source='categories')
#     average_rating = serializers.SerializerMethodField(read_only=True)
#
#     class Meta:
#         model = Book
#         fields = '__all__'
#
#
#     def _update_m2m(self, instance, field_name, through_model, related_field_name, related_instances):
#         """
#         DRY utility method to clear and recreate many-to-many relationships through an intermediate model.
#         """
#         # Clear existing M2M entries
#         getattr(instance, field_name).clear()
#
#         # Recreate through-model relationships
#         for related_instance in related_instances:
#             kwargs = {'book': instance, related_field_name: related_instance}
#             through_model.objects.create(**kwargs)
#
#     def create(self, validated_data):
#         authors = validated_data.pop('authors', [])
#         categories = validated_data.pop('categories', [])
#         book = Book.objects.create(**validated_data)
#
#         self._update_m2m(book, 'authors', BookAuthor, 'author', authors)
#         self._update_m2m(book, 'categories', BookCategory, 'category', categories)
#
#         return book
#
#     def update(self, instance, validated_data):
#         authors = validated_data.pop('authors', None)
#         categories = validated_data.pop('categories', None)
#
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()
#
#         if authors is not None:
#             self._update_m2m(instance, 'authors', BookAuthor, 'author', authors)
#         if categories is not None:
#             self._update_m2m(instance, 'categories', BookCategory, 'category', categories)
#
#         return instance
#
#     @extend_schema_field(serializers.FloatField)
#     def get_average_rating(self, obj):
#             return obj.average_rating()
#
#
# class AuthorSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Author
#         fields = '__all__'
#
#     def validate(self, data):
#         if 'first_name' in data:
#             data['first_name'] = ' '.join(data['first_name'].strip().split()).title()
#         if 'last_name' in data:
#             data['last_name'] = ' '.join(data['last_name'].strip().split()).title()
#         return data
#
#
# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = '__all__'
#
#
# class MemberSerializer(serializers.ModelSerializer):
#     has_overdue = serializers.SerializerMethodField()
#     contact_email = serializers.EmailField(required=True)
#     phone_number = PhoneNumberField(required=True)
#
#     class Meta:
#         model = Member
#         fields = '__all__'
#
#     def get_has_overdue(self, obj):
#         return obj.has_overdue_books()
#
#
#
# class BorrowingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Borrowing
#         fields = '__all__'
#
#     def validate(self, data):
#         borrow_date = data.get('borrow_date')
#         return_date = data.get('return_date')
#         late_fee = data.get('late_fee')
#
#         if return_date and borrow_date and return_date < borrow_date:
#             raise serializers.ValidationError("Return date cannot be before borrow date.")
#
#         if late_fee is not None and late_fee < 0:
#             raise serializers.ValidationError("Late fee cannot be negative.")
#
#         return data
#
#
# class ReviewSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Review
#         fields = '__all__'
#
#     def validate_rating(self, value):
#         if value < 1 or value > 5:
#             raise serializers.ValidationError("Rating must be between 1 and 5.")
#         return value
#
#
# class BookAuthorSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BookAuthor
#         fields = ['book', 'author']
#
#
# class BookCategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BookCategory
#         fields = ['book', 'category']
#
#
#

from .fields import PhoneNumberField
from rest_framework import serializers
from .models import *
from drf_spectacular.utils import extend_schema_field


class AuthorNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['author_id', 'first_name', 'last_name']


class CategoryNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_id', 'category']


class LibrarySerializer(serializers.ModelSerializer):
    contact_email = serializers.EmailField(
        required=True,
        help_text="Official contact email of the library"
    )
    phone_number = PhoneNumberField(
        required=True,
        help_text="Library phone number with country code"
    )

    class Meta:
        model = Library
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    authors = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(), many=True, write_only=True, required=False,
        help_text="List of author IDs"
    )
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, write_only=True, required=False,
        help_text="List of category IDs"
    )
    authors_detail = AuthorNestedSerializer(many=True, read_only=True, source='authors')
    categories_detail = CategoryNestedSerializer(many=True, read_only=True, source='categories')
    average_rating = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Book
        fields = '__all__'

    def _update_m2m(self, instance, field_name, through_model, related_field_name, related_instances):
        """ Utility method for clearing/recreating M2M relationships. """
        getattr(instance, field_name).clear()
        for related_instance in related_instances:
            kwargs = {'book': instance, related_field_name: related_instance}
            through_model.objects.create(**kwargs)

    def create(self, validated_data):
        authors = validated_data.pop('authors', [])
        categories = validated_data.pop('categories', [])
        book = Book.objects.create(**validated_data)
        self._update_m2m(book, 'authors', BookAuthor, 'author', authors)
        self._update_m2m(book, 'categories', BookCategory, 'category', categories)

        return book

    def update(self, instance, validated_data):
        authors = validated_data.pop('authors', None)
        categories = validated_data.pop('categories', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if authors is not None:
            self._update_m2m(instance, 'authors', BookAuthor, 'author_id', authors)
        if categories is not None:
            self._update_m2m(instance, 'categories', BookCategory, 'category_id', categories)

        return instance

    @extend_schema_field(serializers.FloatField)
    def get_average_rating(self, obj):
        return obj.average_rating()


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'

    def validate(self, data):
        if 'first_name' in data:
            data['first_name'] = ' '.join(data['first_name'].strip().split()).title()
        if 'last_name' in data:
            data['last_name'] = ' '.join(data['last_name'].strip().split()).title()
        return data


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class MemberSerializer(serializers.ModelSerializer):
    has_overdue = serializers.SerializerMethodField()
    contact_email = serializers.EmailField(
        required=True, help_text="Member's contact email"
    )
    phone_number = PhoneNumberField(
        required=True, help_text="Member's phone number with country code"
    )

    class Meta:
        model = Member
        fields = '__all__'

    @extend_schema_field(serializers.BooleanField)
    def get_has_overdue(self, obj):
        return obj.has_overdue_books()


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = '__all__'

    def validate(self, data):
        borrow_date = data.get('borrow_date')
        return_date = data.get('return_date')
        late_fee = data.get('late_fee')

        if return_date and borrow_date and return_date < borrow_date:
            raise serializers.ValidationError("Return date cannot be before borrow date.")

        if late_fee is not None and late_fee < 0:
            raise serializers.ValidationError("Late fee cannot be negative.")

        return data


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class BookAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookAuthor
        fields = ['book_id', 'author_id']


class BookCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCategory
        fields = ['book_id', 'category_id']
