from rest_framework import serializers
from votings.models import Character, CharacterVote, Voting


class VotingSerializer(serializers.HyperlinkedModelSerializer):
    votes_amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = Voting
        fields = ['url', 'id', 'title', 'start_date', 'end_date',
                  'max_votes', 'votes_amount']
        

class CharacterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Character
        fields = ['url', 'id', 'last_name', 'first_name', 'second_name', 'age',
                  'description']


class CharacterVoteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CharacterVote
        fields = ['voting', 'character', 'amount']
