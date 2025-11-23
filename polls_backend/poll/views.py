# poll/views.py
from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from polls_backend.poll.utils import rate_limit
from .models import Poll, Question, Choice, Vote
from .serializers import (
    PollListSerializer, PollDetailSerializer,
    QuestionSerializer, ChoiceSerializer, VoteSerializer
)
from .permissions import IsAdminOrReadOnly
from django.db.models import Count
from django.core.cache import cache  # <-- ADDED


class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.all().prefetch_related("questions__choices")
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action in ("list",):
            return PollListSerializer
        return PollDetailSerializer

    # =========================
    # 🔹 Cache Poll List
    # =========================
    def list(self, request, *args, **kwargs):
        cache_key = "poll_list"
        cached = cache.get(cache_key)

        if cached:
            return Response(cached)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=30)   # 30 seconds
        return response

    # =========================
    # 🔹 Cache Poll Detail
    # =========================
    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        cache_key = f"poll_detail_{pk}"

        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=60)
        return response

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            rate_limit(
                user_id=self.request.user.id,
                action="create_poll",
                limit=5,           # max 5 polls
                window_seconds=60  # per minute
            )
        serializer.save(created_by=self.request.user)
        cache.delete("poll_list")  # clear list cache when new poll is added

    # =========================
    # 🔹 Cache Poll Results
    # =========================
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def results(self, request, pk=None):

        cache_key = f"poll_results_{pk}"
        cached = cache.get(cache_key)

        if cached:
            return Response(cached)

        poll = self.get_object()
        questions = poll.questions.prefetch_related('choices__votes').all()

        results = []
        for q in questions:
            choices = q.choices.annotate(votes_count=Count('votes')).values(
                'id', 'text', 'votes_count'
            )
            results.append({
                'question_id': q.id,
                'question_text': q.text,
                'choices': list(choices)
            })

        data = {
            'poll_id': poll.id,
            'title': poll.title,
            'results': results
        }

        cache.set(cache_key, data, timeout=30)  # cache results for 30s
        return Response(data)


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
        user_id = self.request.user.id
        rate_limit(
            user_id=user_id,
            action="vote",
            limit=1,
            window_seconds=10
        )
        vote = serializer.save(user=self.request.user)
        # Invalidate cached results for that specific poll
        poll_id = vote.choice.question.poll_id
        cache.delete(f"poll_results_{poll_id}")

        return vote
