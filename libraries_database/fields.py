import phonenumbers
from rest_framework import serializers

class PhoneNumberField(serializers.CharField):
    def to_internal_value(self, data):
        try:
            parsed = phonenumbers.parse(data, None)
        except phonenumbers.NumberParseException:
            try:
                parsed = phonenumbers.parse(data, "IN")
            except phonenumbers.NumberParseException:
                raise serializers.ValidationError("Could not parse phone number.")
        if not phonenumbers.is_valid_number(parsed):
            raise serializers.ValidationError("Phone number is not valid.")
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
