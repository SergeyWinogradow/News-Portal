# (venv) ~/django-projects/Mac $ python manage.py makemigrations
# (venv) ~/django-projects/Mac $ python manage.py migrate
# (venv) ~/django-projects/Mac $ python manage.py shell

from django.db import models
from django.contrib.auth.models import User

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        post_rating = sum(self.posts.all().values_list('rating', flat=True))
        comment_rating = sum(self.user.comments.all().values_list('rating', flat=True))
        self.rating = post_rating * 3 + comment_rating
        self.save()

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

class Post(models.Model):
    POST_TYPES = (
        ('article', 'Article'),
        ('news', 'News')
    )
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts')
    post_type = models.CharField(max_length=7, choices=POST_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def update_rating(self):
        self.rating = self.likes.all().count() - self.dislikes.all().count()
        self.save()
        self.author.update_rating()

    def preview(self):
        if len(self.text) > 127:
            return self.text[:124] + '...'
        else:
            return self.text

class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_categories')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        self.rating = self.likes.all().count() - self.dislikes.all().count()
        self.save()
        self.post.update_rating()
        self.user.author.update_rating()

    def like(self):
        self.rating += 1
        self.save()
        self.update_rating()

    def dislike(self):
        self.rating -= 1
        self.save()
        self.update_rating()

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')

class Dislike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='dislikes')
