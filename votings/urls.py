from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from votings import views


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'votings', views.VotingViewSet, basename='voting')
router.register(r'characters', views.CharacterViewSet, basename='character')

# The API URLs are now determined automatically by the router.

urlpatterns = [
    path('', include(router.urls)),
    path(
        'votings/<int:pk>/characters/<int:pk_2>/add_vote/',
        views.CharacterVoteView.as_view(),
        name='voting-add-vote'
    ),
    re_path(
        r'media/(?P<file_path>.*?)$',
        views.FileDownloadView.as_view(),
        name='file-download'),
]
