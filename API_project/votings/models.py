from django.db import models


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


def character_image_path(instance, filename: str):
    extension = filename[filename.rfind('.'):]
    return 'character_images/{0}{1}'.format(instance.last_name, extension)


class Character(models.Model):
    last_name = models.CharField(max_length=100, unique=True, blank=False)
    first_name = models.CharField(max_length=100, blank=True)
    second_name = models.CharField(max_length=100, blank=True)
    age = models.IntegerField(blank=True, null=True)
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

    # def __str__(self):
    #     return f'{str(self.id)} | {str(self.voting)} - {str(self.character)}'

    class Meta:
        constraints = [models.UniqueConstraint(fields=['voting', 'character'],
                       name='unique_voting_character')]
