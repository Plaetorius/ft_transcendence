# users/serializers.py
from rest_framework import serializers
from .models import User, Friendship, BlockedUser
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.core.files.uploadedfile import InMemoryUploadedFile

user = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'bio', 'profile_picture', 'profile_picture_url', 'elo')

    def get_profile_picture_url(self, obj):
        if obj.profile_picture and hasattr(obj.profile_picture, 'url'):
            return obj.profile_picture.url
        return None

class UserAllSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'bio', 'profile_picture', 'profile_picture_url', 'elo')

    def get_profile_picture_url(self, obj):
        if obj.profile_picture and hasattr(obj.profile_picture, 'url'):
            return obj.profile_picture.url
        return None

class UserUpdateSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'profile_picture')

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.bio = validated_data.get('bio', instance.bio)
        if 'profile_picture' in validated_data:
            instance.profile_picture = validated_data['profile_picture']
        instance.save()
        return instance

class UserRegistrationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise ValidationError("Email already in use")
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise ValidationError("Username already in use")
        return value

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise ValidationError("Passwords must match")
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username = validated_data['username'],
            email = validated_data['email'],
            password = validated_data['password1'],
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data.get('username'), password=data.get('password'))
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")

class FriendshipSerializer(serializers.ModelSerializer):
    friend1_id = serializers.IntegerField(write_only=True)
    friend2_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Friendship
        fields = ['friend1_id', 'friend2_id']

    def validate_friend1_id(self, value):
        try:
            User.objects.get(pk=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User with id {value} doesn't exist")
        return value

    def validate_friend2_id(self, value):
        try:
            User.objects.get(pk=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User with id {value} doesn't exist")
        return value

    def validate(self, data):
        if data['friend1_id'] == data['friend2_id']:
            raise serializers.ValidationError("You can't be friend with yourself")
        return data

    def create(self, validated_data):
        friend1 = User.objects.get(pk=validated_data['friend1_id'])
        friend2 = User.objects.get(pk=validated_data['friend2_id'])
        return Friendship.objects.create(friend1=friend1, friend2=friend2)

class BlockedUserSerializer(serializers.ModelSerializer):
    blocker_id = serializers.IntegerField(write_only=True)
    blocked_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = BlockedUser
        fields = ['blocker_id', 'blocked_id']

    def validate_blocker_id(self, value):
        try:
            User.objects.get(pk=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User with id {value} doesn't exist")
        return value

    def validate_blocked_id(self, value):
        try:
            User.objects.get(pk=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User with id {value} doesn't exist")
        return value
    
    def validate(self, data):
        if data['blocker_id'] == data['blocked_id']:
            raise serializers.ValidationError("You can't block yourself")
        return data
    
    def create(self, validated_data):
        blocker = User.objects.get(pk=validated_data['blocker_id'])
        blocked = User.objects.get(pk=validated_data['blocked_id'])
        return BlockedUser.objects.create(blocker=blocker, blocked=blocked)
