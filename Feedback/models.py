from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid


class FeedbackForm(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            unique_id = str(uuid.uuid4())[:8]
            self.slug = slugify(self.title) + "-" + unique_id
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Question(models.Model):
    FIELD_TYPES = [
        ("text", "Short Text"),
        ("textarea", "Long Text"),
        ("rating", "Rating"),
        ("number", "Number"),
        ("radio", "Radio Button"),
        ("select", "Dropdown"),
    ]

    form = models.ForeignKey(FeedbackForm, on_delete=models.CASCADE, related_name="questions")
    question_text = models.CharField(max_length=255)
    field_type = models.CharField(max_length=50, choices=FIELD_TYPES)
    required = models.BooleanField(default=True)

    def __str__(self):
        return self.question_text


class Response(models.Model):
    form = models.ForeignKey(FeedbackForm, on_delete=models.CASCADE, related_name="responses")
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response for {self.form.title}"


class Answer(models.Model):
    response = models.ForeignKey(Response, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField()

    def __str__(self):
        return self.answer_text[:50]
