import os
from django.db.models import F, Q, Max
from django.db.models.query import QuerySet
from django.http import FileResponse
from django.utils import timezone
from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.serializers import SerializerMetaclass
from rest_framework.permissions import IsAdminUser
from votings.models import Character, Voting
from votings.permissions import IsStafforReadOnly
from votings.serializers import (CharacterSerializer, CharacterVoteSerializer,
                                 VotingSerializer)
from rest_framework.pagination import PageNumberPagination
from .utilities import is_active_voting
from django.db import transaction


class VotingViewSet(viewsets.ModelViewSet):
    queryset = Voting.objects\
        .prefetch_related('votes')\
        .annotate(leader_votes=Max('votes__amount'))
    serializer_class = VotingSerializer
    permission_classes = [IsStafforReadOnly]

    @action(detail=False)
    def active(self, request, *args, **kwargs):
        now_date = timezone.now().date()
        actual_votings = self.queryset\
            .filter(start_date__lt=now_date, end_date__gte=now_date)
        no_max_votings = actual_votings.filter(max_votes__isnull=True)
        under_max_votings = actual_votings\
            .filter(max_votes__isnull=False)\
            .filter(Q(leader_votes__lt=F('max_votes')) |
                    Q(leader_votes=None))
        query = no_max_votings.union(under_max_votings).order_by('id')

        return self.get_p_response(query, request, VotingSerializer)

    @action(detail=False)
    def finished(self, request, *args, **kwargs):
        now_date = timezone.now().date()
        outdated = self.queryset.filter(end_date__lt=now_date)
        max_votes = self.queryset\
            .filter(start_date__lt=now_date, end_date__gte=now_date)\
            .filter(max_votes__isnull=False)\
            .filter(leader_votes__isnull=False)\
            .filter(leader_votes__gte=F('max_votes'))
        query = outdated.union(max_votes).order_by('id')

        return self.get_p_response(query, request, VotingSerializer)

    @action(detail=True)
    def members(self, request, *args, **kwargs):
        pk = kwargs['pk']
        voting = Voting.objects.filter(id=pk)
        if not voting.exists():
            return Response(
                data={"detail": f"Voting id {pk} does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )

        query = voting.get().characters\
            .prefetch_related('votes')\
            .annotate(votes_amount=F('votes__amount'))

        response = self.get_p_response(query, request, CharacterSerializer)
        if not query.exists():
            response.data['detail'] = f'Voting id {pk} has no members'

        return response

    @action(detail=True)
    def winner(self, request, *args, **kwargs):
        pk = kwargs['pk']
        voting = Voting.objects.filter(id=pk)
        if not voting.exists():
            return Response(
                    data={"detail": f"Voting id {pk} does not exist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        voting = voting.get()
        if is_active_voting(voting):
            return Response(
                data={"detail": f"Voting id {pk} is still active"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        members = voting.votes.all()
        if not members.exists():
            return Response(
                data={"detail": f"Voting id {pk} has no members"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        max_votes = max([i.amount for i in members])
        leaders = [i for i in members if i.amount == max_votes]
        if len(leaders) == 1:
            vote = leaders[0]
            character = vote.character
            character.votes_amount = vote.amount
            serializer = CharacterSerializer(
                character,
                many=False,
                context={"request": request}
            )
            return Response(serializer.data)
        else:
            return Response(
                data={"detail": f"Voting id {pk} members have no leader"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get_p_response(self, query: QuerySet, request: Request,
                       serializer: SerializerMetaclass) -> Response:
        """Rest pagination for additional actions."""
        paginator = PageNumberPagination()
        p_query = paginator.paginate_queryset(query, request)
        serializer = serializer(p_query, many=True,
                                context={'request': request})
        p_response = paginator.get_paginated_response(serializer.data)
        return p_response


class CharacterViewSet(viewsets.ModelViewSet):
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer
    permission_classes = [IsStafforReadOnly]


class CharacterVoteView(APIView):
    def put(self, request, *args, **kwargs):
        pk = kwargs['pk']
        pk_2 = kwargs['pk_2']

        with transaction.atomic():
            voting = Voting.objects.filter(id=pk).select_for_update()
            if not voting.exists():
                return Response(
                    data={"detail": f"Voting id {pk} does not exist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            voting = voting.get()
            if not is_active_voting(voting):
                return Response(
                    data={"detail": f"Voting id {pk} is finished"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            vote = voting.votes.filter(character_id=pk_2)
            if not vote.exists():
                return Response(
                    data={"detail": f"Voting id {pk} has no member id {pk_2}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            vote = vote.get()
            vote.amount += 1
            vote.save()

            serializer = CharacterVoteSerializer(
                vote,
                many=False,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class FileDownloadView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, file_path, *args, **kwargs):
        media_root = settings.MEDIA_ROOT
        full_path = os.path.join(media_root, file_path)
        if os.path.exists(full_path):
            return FileResponse(
                open(full_path, 'rb'),
                as_attachment=True,
            )
        else:
            return Response(
                data={"detail": f"No file {file_path}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
