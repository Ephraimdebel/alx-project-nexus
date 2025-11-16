# poll/views.py
from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Poll, Question, Choice, Vote
from .serializers import (PollListSerializer, PollDetailSerializer,
                          QuestionSerializer, ChoiceSerializer, VoteSerializer)
from .permissions import IsAdminOrReadOnly
from django.shortcuts import get_object_or_404

class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.all().prefetch_related("questions__choices")
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action in ("list",):
            return PollListSerializer
        return PollDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all().select_related("poll").prefetch_related("choices")
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = QuestionSerializer

    def perform_create(self, serializer):
        serializer.save()


class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all().select_related("question")
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = ChoiceSerializer


class VoteCreateAPIView(generics.CreateAPIView):
    """
    Endpoint for voting. Authenticated users only.
    """
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
