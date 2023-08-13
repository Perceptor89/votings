from django.db import models
from votings.utilities import character_image_path
import celery


class Voting(models.Model):
    title = models.CharField(max_length=100, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    max_votes = models.IntegerField(null=True, blank=True)
    characters = models.ManyToManyField('Character', through='CharacterVote')

    def __str__(self) -> str:
        return f'{self.id} | {self.title}'

    class Meta:
        ordering = ['-id']


class Character(models.Model):
    last_name = models.CharField(max_length=100, unique=True, blank=False)
    first_name = models.CharField(max_length=100, blank=True)
    second_name = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(blank=False)
    description = models.TextField(max_length=1000, blank=True)
    photo = models.ImageField(upload_to=character_image_path)

    def __str__(self):
        return f'{str(self.id)} | {self.last_name}'

    class Meta:
        ordering = ['id']


class CharacterVote(models.Model):
    voting = models.ForeignKey('Voting', related_name='votes',
                               on_delete=models.CASCADE)
    character = models.ForeignKey('Character', related_name='votes',
                                  on_delete=models.CASCADE)
    amount = models.IntegerField()

    class Meta:
        constraints = [models.UniqueConstraint(fields=['voting', 'character'],
                       name='unique_voting_character')]


class ExportTask(models.Model):
    execute_at = models.DateTimeField(blank=False)
    e_mail = models.EmailField(blank=False)
    voting = models.ForeignKey('Voting', on_delete=models.DO_NOTHING,
                               blank=False)
    task_id = models.CharField(max_length=100, null=True)
    xlsx = models.FileField(upload_to='reports/', null=True, default=None)

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        if not self.task_id:
            task_id = celery.current_app.send_task(
                args=[self.id],
                name='report',
                eta=self.execute_at,
            )
            self.task_id = task_id
            super(ExportTask, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Reports'
        verbose_name_plural = 'Reports'
