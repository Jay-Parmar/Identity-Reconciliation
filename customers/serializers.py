from rest_framework import serializers
from .models import Contact

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'phoneNumber', 'email', 'linkedId', 'linkPrecedence', 'createdAt', 'updatedAt', 'deletedAt']


class ContactIdentifySerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phoneNumber = serializers.IntegerField(required=False)

    def validate(self, attrs):
        print(attrs)
        if not (attrs.get('email') or attrs.get('phoneNumber')):
            raise serializers.ValidationError("You have to provide any one of the two, i.e., phoneNumber or email")
        serializer = super().validate(attrs)
        return serializer


class ContactReturnSerializer(serializers.Serializer):
    primaryContactId = serializers.IntegerField()
    emails = serializers.ListField(child=serializers.EmailField())
    phoneNumbers = serializers.ListField(child=serializers.IntegerField())
    secondaryContactIds = serializers.ListField(child=serializers.IntegerField())
