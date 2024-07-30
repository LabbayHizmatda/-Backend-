from rest_framework import serializers
from django.contrib.auth import get_user_model  
from .models import CustomUser, Passport, BankCard, Cv, Category, Order, Proposal, Job, Appeal, Review
from .status import RatingChoices

User = get_user_model()


class BankCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankCard
        fields = '__all__'
        extra_kwargs = {
            'owner': {'read_only': True} 
        }

class ReviewSerializer(serializers.ModelSerializer):
    rating = serializers.ChoiceField(choices=RatingChoices.choices, required=False)
    job = serializers.PrimaryKeyRelatedField(queryset=Job.objects.all())

    class Meta:
        model = Review
        fields = ['id', 'owner', 'whom', 'comment', 'rating', 'job']
        extra_kwargs = {
            'owner': {'read_only': True},
            'whom': {'read_only': True}
        }

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        job = validated_data.get('job')

        if 'Customer' in user.roles:
            recipient_user = job.proposal.owner
        elif 'Worker' in user.roles:
            recipient_user = job.order.owner
        else:
            raise serializers.ValidationError("User must be either a Customer or a Worker to create a review.")
        
        try:
            whom = Cv.objects.get(owner=recipient_user) 
        except Cv.DoesNotExist:
            raise serializers.ValidationError("Cv instance for the recipient user does not exist.")
        
        validated_data['owner'] = user
        validated_data['whom'] = whom

        review = Review.objects.create(**validated_data)
        
        whom.update_rating()

        return review

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context['request']
        
        if request.method == 'GET':
            representation.pop('owner', None)
        
        return representation


class CvSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    appeals = serializers.SerializerMethodField()

    class Meta:
        model = Cv
        fields = ['owner', 'image', 'bio', 'rating', 'word_experience', 'reviews', 'appeals']
        extra_kwargs = {
            'owner': {'read_only': True},
            'reviews': {'read_only': True},
            'appeals': {'read_only': True}
        }

    def get_appeals(self, obj):
        # Метод для подсчета количества appeals
        return obj.appeals.count()



class UserSerializer(serializers.ModelSerializer):
    bank_card = BankCardSerializer(read_only=True)
    cv = CvSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            'id', 'user_id', 'first_name', 'last_name', 'full_name', 'password',
            'phone_number', 'birth_date', 'date_created', 'language', 'roles', 'bank_card', 'cv'
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
        user.roles = roles
        user.save()
        return user


class PassportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passport
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


class AppealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appeal
        fields = ['id', 'job', 'problem', 'to', 'owner', 'whom']
        extra_kwargs = {
                'owner': {'read_only': True},
                'whom': {'read_only': True}
            }
    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        job = validated_data.get('job')

        if 'Customer' in user.roles:
            recipient_user = job.proposal.owner
        elif 'Worker' in user.roles:
            recipient_user = job.order.owner
        else:
            raise serializers.ValidationError("User must be either a Customer or a Worker to create a review.")
        
        try:
            whom = Cv.objects.get(owner=recipient_user) 
        except Cv.DoesNotExist:
            raise serializers.ValidationError("Cv instance for the recipient user does not exist.")
        
        validated_data['owner'] = user
        validated_data['whom'] = whom
        
        return super().create(validated_data)
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context['request']
        
        if request.method == 'GET':
            representation.pop('owner', None)
        
        return representation

class JobSerializer(serializers.ModelSerializer):
    appeals = AppealSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Job
        fields = ['id', 'order', 'proposal', 'price', 'status', 'created_at', 'assignee', 'status_history', 'appeals', 'reviews']

