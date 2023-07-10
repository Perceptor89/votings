from django.db.models import F, Sum
from django.http import FileResponse
from django.shortcuts import render
from django.urls import path
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from votings.models import Character, CharacterVote, Voting
from votings.permissions import IsStafforReadOnly
from votings.serializers import (CharacterSerializer, CharacterVoteSerializer,
                                 VotingSerializer)


class VotingViewSet(viewsets.ModelViewSet):
    queryset = Voting.objects\
        .prefetch_related('votes')\
        .annotate(votes_amount=Sum('votes__amount'))
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
            .filter(votes_amount__lt=F('max_votes'))
        query = no_max_votings.union(under_max_votings)
        serializer = VotingSerializer(query, many=True,
                                      context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False)
    def finished(self, request, *args, **kwargs):
        now_date = timezone.now().date()
        outdated = self.queryset.filter(end_date__lt=now_date)
        max_votes = self.queryset\
            .filter(start_date__lt=now_date, end_date__gte=now_date)\
            .filter(votes_amount__gte=F('max_votes'))
        query = outdated.union(max_votes)
        serializer = VotingSerializer(query, many=True,
                                      context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True)
    def characters(self, request, *args, **kwargs):
        pk = kwargs['pk']
        voting = Voting.objects.filter(id=pk)
        if voting.exists():
            query = voting.get().characters
            serializer = CharacterSerializer(
                query,
                many=True,
                context={'request': request},
            )
            if serializer.data:
                return Response(serializer.data)
            else:
                return Response(
                    {"detail": "No members"},
                    status=status.HTTP_204_NO_CONTENT,
                )
        else:
            return Response(
                data={"detail": f"Voting id {pk} does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )

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
        if self.is_active_voting(voting):
            return Response(
                data={"detail": "Voting is still active"},
                status=status.HTTP_204_NO_CONTENT,
            )

        members = voting.votes.all()
        if not members:
            return Response(
                data={"detail": "No voting members"},
                status=status.HTTP_204_NO_CONTENT,
            )

        max_votes = max([i.amount for i in members])
        leader = [i for i in members if i.amount == max_votes]
        if len(leader) == 1:
            leader = leader[0].character
            serializer = CharacterSerializer(
                leader,
                many=False,
                context={"request": request}
            )
            return Response(serializer.data)
        else:
            return Response(
                data={"detail": "Voting members have no leader"},
                status=status.HTTP_204_NO_CONTENT,
            )

    @action(
            methods=['put'],
            detail=False,
            url_path=r'(?P<pk>\w+)/characters/(?P<pk_2>\w+)/add_vote'
        )
    def add_vote(self, request, *args, **kwargs):
        pk = kwargs['pk']
        pk_2 = kwargs['pk_2']
        voting = self.queryset.filter(id=pk)
        if not voting.exists():
            return Response(
                data={"detail": f"Voting id {pk} does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        voting = voting.get()
        if not self.is_active_voting(voting):
            return Response(
                data={"detail": f"Voting id {pk} is inactive"}
            )

        voting_character = voting.votes.filter(character_id=pk_2)
        if not voting_character.exists():
            return Response(
                data={"detail": f"Voting id {pk} has no character id {pk_2}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        voting_character = voting_character.get()
        # if voting.max_votes:
        #     if voting.votes_amount == voting.max_votes:
        #         return Response(
        #             data={"detail": f"Voting id {pk} has max votes amount"},
        #             status=status.HTTP_409_CONFLICT,
        #         )

        voting_character.amount += 1
        voting_character.save()
        serializer = CharacterVoteSerializer(
            voting_character,
            many=False,
            context={'request': request}
        )
        return Response(serializer.data)

    def is_active_voting(self, voting: Voting) -> bool:
        now_date = timezone.now().date()
        member_votes = voting.votes.all()

        if voting.end_date >= now_date:
            if not voting.max_votes:
                return True
            elif not member_votes.exists():
                return True
            else:
                total_votes = sum([i.amount for i in member_votes])
                if total_votes < voting.max_votes:
                    return True
        else:
            return False


class CharacterViewSet(viewsets.ModelViewSet):
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer
    permission_classes = [IsStafforReadOnly]

    @action(methods=['get'], detail=True)
    def get_img(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                data={"detail": "You need to be a staff member"},
                status=status.HTTP_403_FORBIDDEN,
            )

        pk = kwargs['pk']
        character = self.queryset.filter(id=pk)
        if not character.exists():
            return Response(
                data={"detail": f"Character id {pk} does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        character = character.get()
        return FileResponse(character.photo.file)
