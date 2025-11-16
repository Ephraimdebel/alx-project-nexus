# poll/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Poll, Question, Choice, Vote

User = get_user_model()


class ChoiceSerializer(serializers.ModelSerializer):
    votes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Choice
        fields = ("id", "text", "votes_count")

    def get_votes_count(self, obj):
        return obj.votes.count()


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    choices_count = serializers.IntegerField(source="choices.count", read_only=True)

    class Meta:
        model = Question
        fields = ("id", "text", "choices", "choices_count")


class PollListSerializer(serializers.ModelSerializer):
    questions_count = serializers.IntegerField(source="questions.count", read_only=True)

    class Meta:
        model = Poll
        fields = ("id", "title", "description", "created_by", "created_at", "questions_count")


class PollDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    created_by_username = serializers.ReadOnlyField(source="created_by.username")

    class Meta:
        model = Poll
        fields = ("id", "title", "description", "created_by", "created_by_username",
                  "created_at", "expires_at", "questions")


class VoteSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())
    choice = serializers.PrimaryKeyRelatedField(queryset=Choice.objects.all())

    class Meta:
        model = Vote
        fields = ("id", "user", "question", "choice", "created_at")
        read_only_fields = ("created_at",)

    def validate(self, attrs):
        # Ensure the choice belongs to the question
        choice = attrs.get("choice")
        question = attrs.get("question")
        if choice.question_id != question.id:
            raise serializers.ValidationError({"choice": "This choice does not belong to the given question."})

        # Ensure the user hasn't already voted on this question
        user = self.context["request"].user
        if Vote.objects.filter(user=user, question=question).exists():
            raise serializers.ValidationError({"non_field_errors": "You have already voted for this question."})

        return attrs
