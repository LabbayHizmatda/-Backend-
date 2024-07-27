from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CustomUser, Passport, BankCard, Cv, Category, Order, Proposal, Job
from .status import RoleChoices


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    roles = serializers.ListField(
        child=serializers.ChoiceField(choices=RoleChoices.choices),
        write_only=True,
        required=True
    )

    class Meta:
        model = CustomUser
        fields = (
            'id', 'user_id', 'first_name', 'last_name', 'full_name', 'password',
            'roles', 'phone_number', 'birth_date', 'date_created', 'language'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        roles = validated_data.pop('roles', [])
        user = CustomUser.objects.create_user(
            user_id=validated_data['user_id'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', None),
            birth_date=validated_data.get('birth_date', None),
            language=validated_data.get('language', None),
        )
        user.roles = roles  # Save roles directly
        user.save()
        return user


class PassportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passport
        fields = '__all__'
        extra_kwargs = {
            'owner': {'read_only': True} 
        }

class BankCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankCard
        fields = '__all__'
        extra_kwargs = {
            'owner': {'read_only': True} 
        }

class CvSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cv
        fields = '__all__'
        extra_kwargs = {
                'owner': {'read_only': True} 
            }

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = '__all__'
        extra_kwargs = {
            'owner': {'read_only': True} 
        }

class OrderSerializer(serializers.ModelSerializer):
    proposals = ProposalSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'description', 'image', 'location', 'location_link', 'price', 'status', 'created_at', 'owner', 'category', 'proposals']
        extra_kwargs = {
            'owner': {'read_only': True} 
        }


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'

