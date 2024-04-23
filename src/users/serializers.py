# users/serializers.py
from rest_framework import serializers
from django.templatetags.static import static
from django.conf import settings
from .models import User, Friendship, BlockedUser, MatchHistory, PlayerMatchHistory
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import RegexValidator
from django.core.files.storage import default_storage
from django.core.cache import cache
import bleach
import re


user = get_user_model()

username_validator = RegexValidator(
    regex=r'^[a-zA-Z][a-zA-Z0-9_-]*$',
    message="Username must start with a letter and can only contain letters, numbers, underscores and hyphens.",
)

first_name_validator = RegexValidator(
    regex=r'^[a-zA-Z]+(?:[-\'\s][a-zA-Z]+)*$|^$',
    message="First name must only contain letters, spaces, hyphens, or apostrophes, or be empty.",
)

last_name_validator = RegexValidator(
    regex=r'^[a-zA-Z]+(?:[-\'\s][a-zA-Z]+)*$|^$',
    message="Last name must only contain letters, spaces, hyphens, or apostrophes, or be empty.",
)

def sanitize_bio(value):
    clean_bio = bleach.clean(value, tags=[], strip=True)
    return clean_bio

def validate_image(file):
    valid_extensions = ['jpg', 'jpeg', 'png']
    extension = file.name.rsplit('.', 1)[1].lower()
    filename = file.name.rsplit('/', 1)[-1]

    if filename == "default.jpg":
        raise ValidationError('The file name "default.jpg" is reserved and cannot be used.')

    if extension not in valid_extensions:
        raise ValidationError('Unsupported file extension.')
    
    max_size = 4 * 1024 * 1024  # Max size 4MB
    if file.size > max_size:
        raise ValidationError('Image file too large ( > 4MB)')

class UserSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()
    username = serializers.CharField(validators=[username_validator])
    bio = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'bio', 'profile_picture', 'profile_picture_url', 'elo', 'is_online', 'date_joined')

    def validate_bio(self, value):
        return sanitize_bio(value)

    def get_profile_picture_url(self, obj):
        if obj.profile_picture and hasattr(obj.profile_picture, 'url'):
            return obj.profile_picture.url
        return static('../media/profile_pictures/default.jpg') # Shouldn't happen, if user removes pp in edit => should give the base one


class UserAllSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()
    username = serializers.CharField(validators=[username_validator])
    first_name = serializers.CharField(validators=[first_name_validator])
    last_name = serializers.CharField(validators=[last_name_validator])
    bio = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'bio', 'profile_picture', 'profile_picture_url', 'elo')

    def validate_bio(self, value):
        return sanitize_bio(value)

    def get_profile_picture_url(self, obj):
        if obj.profile_picture and hasattr(obj.profile_picture, 'url'):
            return obj.profile_picture.url
        return None


class UserUpdateSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False, validators=[validate_image])
    username = serializers.CharField(validators=[username_validator])
    first_name = serializers.CharField(required=False, default='', allow_blank=True, trim_whitespace=True, validators=[first_name_validator])
    last_name = serializers.CharField(required=False, default='', allow_blank=True, trim_whitespace=True, validators=[last_name_validator])
    bio = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'profile_picture')

    def validate_bio(self, value):
        return sanitize_bio(value)

    def validate_username(self, value):
        if self.instance.username != value:
            if hasattr(self.instance, 'oauth_cred') and self.instance.oauth_cred:
                raise serializers.ValidationError("You cannot change your username because your account is linked with OAuth.")
            if value == "default":
                raise serializers.ValidationError("Username 'default' is reserved.")
            if User.objects.exclude(pk=self.instance.pk).filter(username=value).exists():
                raise serializers.ValidationError("This username is already in use.")
        return value

    def validate_email(self, value):
        if self.instance.email.lower() != value.lower():
            if hasattr(self.instance, 'oauth_cred') and self.instance.oauth_cred:
                raise serializers.ValidationError("You cannot change your email because your account is linked with OAuth.")
            if value.lower().endswith("@student.42.fr"):
                raise serializers.ValidationError("Using '@student.42.fr' emails is not allowed for registration or updates.")
            if User.objects.exclude(pk=self.instance.pk).filter(email__iexact=value).exists():
                raise serializers.ValidationError("This email is already in use by another user.")
        return value

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.bio = validated_data.get('bio', instance.bio)


        if 'profile_picture' in validated_data:
            if instance.profile_picture and hasattr(instance.profile_picture, 'url'):
                if not instance.profile_picture.name.endswith("default.jpg"):
                    try:
                        picture_path = instance.profile_picture.path
                        if default_storage.exists(picture_path):
                            default_storage.delete(picture_path)
                    except Exception as e:
                        print(f"Error deleting old profile picture: {e}")
            # Assign the new picture
            instance.profile_picture = validated_data['profile_picture']
        instance.save()
        return instance

class UserRegistrationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(required=True, validators=[username_validator])
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def validate_email(self, value):
        oauth_linked = hasattr(self.instance, 'oauth_credentials') and self.instance.oauth_credentials is not None
        if not oauth_linked and value.lower().endswith("@student.42.fr"):
            raise ValidationError("Registration using '@student.42.fr' emails is not allowed.")
        if User.objects.filter(email__iexact=value).exists():
            raise ValidationError("This email is already in use.")
        return value
    
    def validate_username(self, value):
        if value == "default":
            raise ValidationError("Username 'default' is reserved.")
        if User.objects.filter(username=value).exists():
            raise ValidationError("This username is already in use.")
        return value

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise ValidationError("Passwords must match!")
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
        user = authenticate(username=username, password=data.get('password'))
        if user is None:
            raise serializers.ValidationError("Incorrect username or password.")
        return user

class FriendshipDetailSerializer(serializers.ModelSerializer):
    friend_details = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ['friend_details']

    def get_friend_details(self, obj):
        request_user = self.context.get('request_user')
        friend = obj.friend1 if obj.friend1 != request_user else obj.friend2
        return UserSerializer(friend).data

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

class PlayerMatchHistorySerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='player.username')
    
    class Meta:
        model = PlayerMatchHistory
        fields = ('username', 'score', 'elo_change')

class MatchHistorySerializer(serializers.ModelSerializer):
    players = PlayerMatchHistorySerializer(source='playermatchhistory_set', many=True)
    game_type = serializers.CharField()
    duration = serializers.DurationField()
    date_played = serializers.DateTimeField()

    class Meta:
        model = MatchHistory
        fields = ('game_type', 'duration', 'date_played', 'players')

class PlayerRankSerializer(serializers.ModelSerializer):
    win_rate = serializers.SerializerMethodField()
    rank = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'elo', 'win_rate', 'rank')

    def get_win_rate(self, obj):
        return obj.win_rate()

    def get_rank(self, obj):
        users_with_higher_elo = User.objects.filter(elo__gt=obj.elo).count()
        return users_with_higher_elo + 1