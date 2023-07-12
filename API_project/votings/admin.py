from django.contrib import admin
from .models import Voting, Character, CharacterVote
from django.db.models import Max


@admin.register(Voting)
class VotingAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'start_date', 'end_date', 'max_votes',
                    'leader_votes']
    empty_value_display = "not set"
    list_display_links = ['title']

    @admin.display(empty_value=0)
    def leader_votes(self, obj):
        return obj.votes.aggregate(leader_votes=Max('amount'))['leader_votes']


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ['id', 'last_name', 'first_name', 'second_name',
                    'age', 'description']
    empty_value_display = "not set"
    list_display_links = ['last_name']


@admin.register(CharacterVote)
class CharacterVoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'voting', 'character', 'amount']
    list_display_links = ['id']
