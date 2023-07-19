import logging

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage

from API_project.celery import app
from votings.models import ExportTask
from votings.utilities import create_report_xlsx, is_active_voting


@app.task(name='report')
def send_report(export_task_id: int):
    """Sends an xlsx voting report by email ExportTask is created."""
    export_task = ExportTask.objects.filter(id=export_task_id).get()
    voting = export_task.voting

    is_active = is_active_voting(voting)
    max_condition = voting.max_votes if voting.max_votes else 'no'
    attachment_str: str | None = None
    attachment_file: str | None = None
    if voting.votes.exists():
        file_name = f'voting_{voting.id}_members.xlsx'
        try:
            data = create_report_xlsx(voting.votes.order_by('-amount'))
            file = ContentFile(content=data, name=file_name)
            export_task.xlsx.save(name=file_name, content=file)
            attachment_str = 'See information about members in attachment.'
            attachment_file = export_task.xlsx.path
        except Exception:
            logging.warning(f'Couldn\'t create xlsx for {export_task_id}')
            return
    else:
        attachment_str = 'Voting has no members.'

    message = ('Hi! This is your voting report:\n\n'
               f'ID:                {voting.id}\n'
               f'Title:             {voting.title}\n'
               f'Start date:        {voting.start_date}\n'
               f'End date:          {voting.end_date}\n'
               f'Max condition:     {max_condition}\n'
               f'Is active:         {is_active}\n\n'
               f'{attachment_str}')

    email = EmailMessage(
        subject=f'Voting {voting.id} report',
        from_email=settings.EMAIL_HOST_USER,
        body=message,
        to=[export_task.e_mail],
        reply_to=[]
    )

    if attachment_file:
        email.attach_file(attachment_file)

    email.send()
