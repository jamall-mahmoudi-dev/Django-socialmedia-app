from rest_framework import serializers
from .models import Profile, Post, Liked_Post, Comment, Follow
from django.contrib.auth.models import User

#  سریالایزر User
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']

#  سریالایزر Profile (جزئیات کامل)
class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    username = serializers.ReadOnlyField(source='user.username')
    followers_count = serializers.IntegerField(source='followers', read_only=True)
    following_count = serializers.IntegerField(source='following', read_only=True)
    is_followed = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = [
            'id', 'user', 'username', 'bio', 'profile_img', 
            'location', 'followers_count', 'following_count',
            'is_followed'
        ]
    
    def get_is_followed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(
                current_user=request.user, 
                followed=obj
            ).exists()
        return False

#  سریالایزر Comment
class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.user.username')
    author_profile_img = serializers.ReadOnlyField(source='author.profile_img.url')
    
    class Meta:
        model = Comment
        fields = [
            'id', 'post_id', 'content', 'author', 
            'author_username', 'author_profile_img'
        ]
        read_only_fields = ['author']

#  سریالایزر Post (با جزئیات کامل)
class PostSerializer(serializers.ModelSerializer):
    profile_username = serializers.ReadOnlyField(source='Profile.user.username')
    profile_img = serializers.ReadOnlyField(source='Profile.profile_img.url')
    comments = CommentSerializer(many=True, read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    is_liked = serializers.SerializerMethodField()
    time_formatted = serializers.DateTimeField(source='time', format='%Y-%m-%d %H:%M')
    
    class Meta:
        model = Post
        fields = [
            'post_id', 'Profile', 'profile_username', 'profile_img',
            'Img', 'caption', 'time', 'time_formatted', 
            'likes', 'comments', 'comments_count', 'is_liked'
        ]
        read_only_fields = ['post_id', 'time', 'likes']
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Liked_Post.objects.filter(
                Username=request.user.username,
                post_id=obj.post_id
            ).exists()
        return False

#  سریالایزر ساده برای ایجاد/ویرایش پست
class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['caption', 'Img', 'Profile']
        read_only_fields = ['post_id', 'time', 'likes']
    
    def validate_caption(self, value):
        if len(value.strip()) < 1:
            raise serializers.ValidationError("متن پست نمی‌تواند خالی باشد")
        return value

#  سریالایزر Like
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Liked_Post
        fields = ['Username', 'post_id']
    
    def validate(self, data):
        # بررسی اینکه پست وجود دارد
        if not Post.objects.filter(post_id=data['post_id']).exists():
            raise serializers.ValidationError("پست مورد نظر یافت نشد")
        return data

#  سریالایزر Follow
class FollowSerializer(serializers.ModelSerializer):
    followed_username = serializers.ReadOnlyField(source='followed.user.username')
    followed_profile_img = serializers.ReadOnlyField(source='followed.profile_img.url')
    
    class Meta:
        model = Follow
        fields = ['id', 'current_user', 'followed', 'followed_username', 'followed_profile_img']
        read_only_fields = ['current_user']