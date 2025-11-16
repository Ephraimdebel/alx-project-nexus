# poll/admin.py
from django.contrib import admin
from .models import Poll, Question, Choice, Vote

@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_by", "created_at")

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "poll")

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "question")

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "question", "choice", "created_at")
