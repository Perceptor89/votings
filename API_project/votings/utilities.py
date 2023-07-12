from .models import Voting
from django.utils import timezone


def is_active_voting(voting: Voting) -> bool:
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
            if leader_votes < voting.max_votes:
                return True
    else:
        return False
