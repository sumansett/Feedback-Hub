from django.contrib import admin
from .models import FeedbackForm, Question, Response, Answer


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


class FeedbackFormAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "created_at")
    search_fields = ("title", "owner__username")
    list_filter = ("created_at",)
    inlines = [QuestionInline]


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0


class ResponseAdmin(admin.ModelAdmin):
    list_display = ("form", "name", "email", "submitted_at")
    search_fields = ("name", "email", "form__title")
    list_filter = ("submitted_at",)
    inlines = [AnswerInline]


admin.site.register(FeedbackForm, FeedbackFormAdmin)
admin.site.register(Question)
admin.site.register(Response, ResponseAdmin)
admin.site.register(Answer)