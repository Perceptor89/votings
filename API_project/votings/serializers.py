from rest_framework import serializers
from votings.models import Character, CharacterVote, Voting


class VotingSerializer(serializers.HyperlinkedModelSerializer):
    leader_votes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Voting
        fields = ['url', 'id', 'title', 'start_date', 'end_date',
                  'max_votes', 'leader_votes']


class CharacterSerializer(serializers.HyperlinkedModelSerializer):
    votes_amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = Character
        fields = ['url', 'id', 'last_name', 'first_name', 'second_name', 'age',
                  'description', 'votes_amount']


class CharacterVoteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CharacterVote
        fields = ['voting', 'character']
