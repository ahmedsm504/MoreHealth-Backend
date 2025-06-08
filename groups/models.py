from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth.models import User 
from taggit.managers import TaggableManager


User = get_user_model()

def upload_to(instance, filename):
    return 'groups/images/{filename}'.format(filename=filename)


class Group(models.Model):
    name = models.CharField("اسم المجموعة", max_length=100, unique=True)
    description = models.TextField("الوصف")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(User, related_name='joined_groups')
    tags = TaggableManager("tags", blank=True)
    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    image = models.ImageField("صورة المجموعة", upload_to=upload_to, blank=True)

    def get_absolute_url(self):
        return reverse('groups:detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name

class Question(models.Model):
    title = models.CharField("العنوان", max_length=200)
    content = models.TextField("المحتوى")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='questions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    created_at = models.DateTimeField("تاريخ النشر", auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)    
    upvotes = models.ManyToManyField(User, related_name='upvoted_questions', blank=True)

    class Meta:
        ordering = ['-created_at']

    def total_upvotes(self):
        return self.upvotes.count()

class Comment(models.Model):
    content = models.TextField("التعليق")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')  # لدعم الردود
    created_at = models.DateTimeField("تاريخ التعليق", auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    upvotes = models.ManyToManyField(User, related_name='upvoted_comments', blank=True)

    def total_upvotes(self):
        return self.upvotes.count()

    def is_reply(self):
        return self.parent is not None  # للتحقق إذا كان هذا تعليقًا أم ردًا
