from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import TransportRecord

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')
        extra_kwargs = {
            'email': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user
    
class TransportRecordSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    dh_miles = serializers.FloatField()
    miles = serializers.FloatField()
    fuel = serializers.FloatField()
    food = serializers.FloatField()
    lumper = serializers.FloatField()
    pay = serializers.FloatField()

    class Meta:
        model = TransportRecord
        fields = ['id', 'user', 'date', 'po_number', 'location_from', 'location_to', 
                  'dh_miles', 'miles', 'fuel', 'food', 'lumper', 'pay']
        read_only_fields = ['id', 'user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)