from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CustomUser, Passport, BankCard, Cv, Category, Order, Proposal, Job, Appeal, Review, Image, Video
from .status import RatingChoices
from django.contrib.auth.hashers import make_password

User = get_user_model()

class BankCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankCard
        fields = '__all__'
        extra_kwargs = {
            'owner': {'read_only': True}
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if self.context.get('hide_owner'):
            representation.pop('owner', None)
        return representation


class ReviewSerializer(serializers.ModelSerializer):
    rating = serializers.ChoiceField(choices=RatingChoices.choices, required=False)
    job = serializers.PrimaryKeyRelatedField(queryset=Job.objects.all())
    whom = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'owner', 'whom', 'comment', 'rating', 'job']
        extra_kwargs = {
            'owner': {'read_only': True},
            'whom': {'read_only': True}
        }

    def get_whom(self, obj):
        return obj.whom.owner.user_id if obj.whom else None

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

        whom = Cv.objects.filter(owner=recipient_user).first()
        if not whom:
            raise serializers.ValidationError("Cv instance for the recipient user does not exist.")
        
        validated_data['owner'] = user
        validated_data['whom'] = whom

        review = Review.objects.create(**validated_data)
        whom.update_rating()
        return review

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if self.context.get('hide_owner'):
            representation.pop('owner', None)
        return representation


class CvSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    appeals = serializers.SerializerMethodField()

    class Meta:
        model = Cv
        fields = ['owner', 'image', 'bio', 'rating', 'word_experience', 'appeals', 'reviews']
        extra_kwargs = {
            'owner': {'read_only': True},
            'reviews': {'read_only': True},
            'appeals': {'read_only': True}
        }

    def get_appeals(self, obj):
        return obj.appeals.count()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if self.context.get('hide_owner'):
            representation.pop('owner', None)
        return representation


class UserSerializer(serializers.ModelSerializer):
    bank_card = BankCardSerializer(read_only=True)
    cv = CvSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            'id', 'user_id', 'first_name', 'last_name', 'full_name', 'password',
            'phone_number', 'birth_date', 'date_created', 'language', 'roles', 'bank_card', 'cv'
        )
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'user_id': {'required': True}
        }

    def create(self, validated_data):
        roles = validated_data.pop('roles', [])

        validated_data['password'] = make_password(validated_data['password'])

        user = CustomUser.objects.create(
            user_id=validated_data['user_id'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', None),
            birth_date=validated_data.get('birth_date', None),
            language=validated_data.get('language', None),
            roles=roles 
        )

        return user


class PassportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passport
        fields = '__all__'
        extra_kwargs = {
            'owner': {'read_only': True}
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if self.context.get('hide_owner'):
            representation.pop('owner', None)
        return representation


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = ['id', 'order', 'message', 'price', 'status', 'created_at', 'owner']
        extra_kwargs = {
            'order': {'required': True},
            'owner': {'read_only': True}
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if self.context.get('hide_owner'):
            representation.pop('owner', None)
        return representation


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image_file']


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'video_file']


class OrderSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    videos = VideoSerializer(many=True, read_only=True)
    image_files = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)
    video_files = serializers.ListField(child=serializers.FileField(), write_only=True, required=False)
    proposals = ProposalSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'description', 'location', 'location_link', 'price', 'status', 'created_at', 'owner', 'category', 'images', 'videos', 'image_files', 'video_files', 'proposals']
        extra_kwargs = {
            'owner': {'read_only': True}
        }

    def create(self, validated_data):
        image_files = validated_data.pop('image_files', [])
        video_files = validated_data.pop('video_files', [])
        
        order = super().create(validated_data)

        for image in image_files:
            Image.objects.create(order=order, image_file=image)
        for video in video_files:
            Video.objects.create(order=order, video_file=video)
        
        return order
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if self.context.get('hide_owner'):
            representation.pop('owner', None)
        return representation


class AppealSerializer(serializers.ModelSerializer):
    whom = serializers.SerializerMethodField()

    class Meta:
        model = Appeal
        fields = ['id', 'job', 'problem', 'to', 'owner', 'whom']
        extra_kwargs = {
            'owner': {'read_only': True},
            'whom': {'read_only': True}
        }

    def get_whom(self, obj):
        return obj.whom.owner.user_id if obj.whom else None

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        job = validated_data.get('job')

        if 'Customer' in user.roles:
            recipient_user = job.proposal.owner
        elif 'Worker' in user.roles:
            recipient_user = job.order.owner
        else:
            raise serializers.ValidationError("User must be either a Customer or a Worker to create an appeal.")
        
        whom = Cv.objects.filter(owner=recipient_user).first()
        if not whom:
            raise serializers.ValidationError("Cv instance for the recipient user does not exist.")
        
        validated_data['owner'] = user
        validated_data['whom'] = whom
        
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if self.context.get('hide_owner'):
            representation.pop('owner', None)
        return representation


class JobSerializer(serializers.ModelSerializer):
    appeals = AppealSerializer(many=True, required=False, allow_null=True)
    reviews = ReviewSerializer(many=True, required=False, allow_null=True)
    
    class Meta:
        model = Job
        fields = ['id', 'order', 'proposal', 'price', 'status', 'created_at', 'assignee',\
                  'status_history', 'appeals', 'reviews', 'payment_confirmed_by_customer',\
                  'payment_confirmed_by_worker', 'review_written_by_worker', 'review_written_by_customer']
