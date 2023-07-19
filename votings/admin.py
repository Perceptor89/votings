from typing import Any

from django.contrib import admin
from django.db.models import Max
from votings.forms import CharacterForm, ExportTaskForm, VotingForm

from .models import Character, CharacterVote, ExportTask, Voting
from celery.result import AsyncResult
from votings.utilities import calculate_age


@admin.register(Voting)
class VotingAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'start_date', 'end_date', 'max_votes',
                    'leader_votes']
    empty_value_display = "not set"
    list_display_links = ['title']
    form = VotingForm

    @admin.display(empty_value=0)
    def leader_votes(self, obj):
        return obj.votes.aggregate(leader_votes=Max('amount'))['leader_votes']


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ['id', 'last_name', 'first_name', 'second_name',
                    'age', 'description', 'photo']
    empty_value_display = "not set"
    list_display_links = ['last_name']
    form = CharacterForm

    @admin.display
    def age(self, obj: Character) -> int:
        return calculate_age(obj.birth_date)


@admin.register(CharacterVote)
class CharacterVoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'voting', 'character', 'amount']
    list_display_links = ['id']
    list_filter = ['voting__title']


@admin.register(ExportTask)
class ExportTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'execute_at', 'e_mail', 'voting', 'status', 'xlsx']
    list_display_links = ['e_mail']
    form = ExportTaskForm

    @admin.display
    def status(self, obj: ExportTask) -> str:
        state = AsyncResult(obj.task_id).state if obj.task_id else 'PENDING'
        return state

    def get_form(self, request, *args, **kwargs) -> Any:
        form = super(ExportTaskAdmin, self).get_form(request, **kwargs)
        user_email = request.user.email
        form.base_fields['e_mail'].initial = user_email

        return form
