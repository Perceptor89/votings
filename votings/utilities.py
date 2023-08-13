from datetime import datetime
import io
from django.utils import timezone
from django.db.models import QuerySet
import pandas as pd
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from votings.models import Voting, Character


def is_active_voting(voting: 'Voting') -> bool:
    """
        Checking that
            voting has actual dates
            leader votes is under max parameter, if it was set.
    """
    now_date = timezone.now().date()
    member_votes = voting.votes.all()

    if voting.start_date < now_date <= voting.end_date:
        if not voting.max_votes:
            return True
        elif not member_votes.exists():
            return True
        else:
            leader_votes = max([i.amount for i in member_votes])
            return True if leader_votes < voting.max_votes else False
    else:
        return False


def character_image_path(instance: 'Character', filename: str):
    extension = filename[filename.rfind('.'):]
    return 'character_images/{0}{1}'.format(instance.last_name, extension)


def create_report_xlsx(votes: QuerySet) -> bytes:
    df = pd.DataFrame(
        {
            'Last name': [vote.character.last_name for vote in votes],
            'Votes': [vote.amount for vote in votes],
        }
    )

    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Members')
    writer.close()

    return output.getvalue()


def calculate_age(birth_date: datetime) -> int:
    today = timezone.now().date()
    return today.year - birth_date.year - (
        (today.month, today.day) <= (birth_date.month, birth_date.day)
    )
