# poll/urls.py
from rest_framework import routers
from django.urls import path, include
from .views import PollViewSet, QuestionViewSet, ChoiceViewSet, VoteCreateAPIView

router = routers.DefaultRouter()
router.register(r"polls", PollViewSet, basename="polls")
router.register(r"questions", QuestionViewSet, basename="questions")
router.register(r"choices", ChoiceViewSet, basename="choices")

urlpatterns = [
    path("", include(router.urls)),
    path("vote/", VoteCreateAPIView.as_view(), name="vote"),
]
