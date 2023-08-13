from datetime import datetime

from django import forms
from django.utils import timezone

from votings.models import Character, ExportTask, Voting
from votings.utilities import calculate_age


class ExportTaskForm(forms.ModelForm):
    class Meta:
        model = ExportTask
        fields = ['execute_at', 'voting', 'e_mail']

    def is_valid(self) -> bool:
        date_str = self.data.get('execute_at_0')
        time_str = self.data.get('execute_at_1')
        if '' not in [date_str, time_str]:
            year, month, day = [int(v) for v in date_str.split('-')]
            hour, mins, secs = [int(v) for v in time_str.split(':')]
            now = timezone.now()
            execute_at = datetime(year, month, day, hour, mins, secs,
                                  tzinfo=now.tzinfo)
            if now >= execute_at:
                self.add_error('execute_at', 'Datetime must be later than now')

        return super().is_valid()


class CharacterForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = ['last_name', 'first_name', 'second_name', 'birth_date',
                  'description', 'photo']

    def is_valid(self) -> bool:
        birth_date = self.data.get('birth_date')
        if birth_date:
            try:
                birth_date = datetime.strptime(birth_date, '%Y-%m-%d')
                age = calculate_age(birth_date)
                if age < 18:
                    self.add_error('birth_date',
                                   'Character must be at least 18 years old.')
            except ValueError:
                pass
        return super().is_valid()


class VotingForm(forms.ModelForm):
    class Meta:
        model = Voting
        fields = ['title', 'start_date', 'end_date', 'max_votes']

    def is_valid(self) -> bool:
        try:
            start_date = self.data.get('start_date')
            end_date = self.data.get('end_date')

            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

            if start_date >= end_date:
                self.add_error(
                    'start_date',
                    'The start date must be earlier than the end date.'
                )
        except ValueError:
            pass

        return super().is_valid()
