from datetime import datetime
import os
from django.test import TestCase
from ..models import Voting, Character, CharacterVote
from freezegun import freeze_time
from django.urls import reverse
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.models import User
import io
from django.conf import settings


class TestVotings(TestCase):
    fixtures_path = os.path.join(
        settings.BASE_DIR,
        'votings/tests/fixtures/instances.json',
    )
    fixtures = [fixtures_path]

    def setUp(self) -> None:
        self.media_root = settings.MEDIA_ROOT
        self.active_title = 'Самый быстрый'
        self.finished_title = 'Самый сильный'
        self.future_title = 'Самый смелый'

        self.voting_1 = Voting.objects.get(id=1)
        self.voting_2 = Voting.objects.get(id=2)
        self.voting_3 = Voting.objects.get(id=3)
        self.character_1 = Character.objects.get(id=1)
        self.character_2 = Character.objects.get(id=2)
        self.character_3 = Character.objects.get(id=3)

        self.admin = User.objects.create_superuser(
            'admin',
            'test@mail.ru',
            'secret',
        )

        return super().setUp()

    def test_voting_list(self):
        response = self.client.get(reverse('voting-list'))
        self.assertEqual(response.status_code, 200)
        titles = [v['title'] for v in response.json()['results']]
        target_list = [self.active_title, self.finished_title,
                       self.future_title]
        self.assertEqual(titles, target_list)

    def test_no_voting(self):
        Voting.objects.all().delete()
        response = self.client.get(reverse('voting-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['results'], [])

    @freeze_time('2023-07-09')
    def test_voting_active(self):
        # Also check is_limit_no_members case
        response = self.client.get(reverse('voting-active'))
        self.assertEqual(response.status_code, 200)
        titles = [v['title'] for v in response.json()['results']]
        self.assertEqual([self.active_title], titles)
        self.assertNotIn(self.finished_title, titles)
        self.assertNotIn(self.future_title, titles)

    @freeze_time('2023-07-09')
    def test_voting_no_active(self):
        Voting.objects.all().delete()
        response = self.client.get(reverse('voting-active'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['results'], [])

    @freeze_time('2023-07-09')
    def test_voting_starts_today(self):
        voting = Voting.objects.create(
            title='Еще одно', start_date='2023-07-09', end_date='2023-07-15'
        )
        response = self.client.get(reverse('voting-active'))
        self.assertEqual(response.status_code, 200)
        active_titles = [v['title'] for v in response.json()['results']]
        self.assertNotIn(voting.title, active_titles)

    @freeze_time('2023-07-09')
    def test_voting_ends_today(self):
        # Also check no_limit_no_members case
        voting = Voting.objects.create(
            title='Еще одно', start_date='2023-07-01', end_date='2023-07-09'
        )
        response = self.client.get(reverse('voting-active'))
        self.assertEqual(response.status_code, 200)
        active_titles = [v['title'] for v in response.json()['results']]
        self.assertIn(voting.title, active_titles)

    @freeze_time('2023-07-09')
    def test_voting_not_actual_date(self):
        # Also check no_limit_no_members case
        now = timezone.now().date()
        self.assertGreater(now, self.voting_2.end_date)
        self.assertLess(now, self.voting_3.start_date)
        response = self.client.get(reverse('voting-active'))
        self.assertEqual(response.status_code, 200)
        active_titles = [v['title'] for v in response.json()['results']]
        self.assertNotIn(self.voting_2.title, active_titles)
        self.assertNotIn(self.voting_3.title, active_titles)

    @freeze_time('2023-07-09')
    def test_voting_no_limit_with_members(self):
        voting = Voting.objects.create(
            title='Еще одно', start_date='2023-07-08', end_date='2023-07-22'
        )
        CharacterVote.objects.create(voting=voting, character=self.character_1,
                                     amount=10)
        response = self.client.get(reverse('voting-active'))
        self.assertEqual(response.status_code, 200)
        active_titles = [v['title'] for v in response.json()['results']]
        self.assertIn(voting.title, active_titles)

    @freeze_time('2023-07-09')
    def test_voting_is_limit_under_max_votes(self):
        self.assertIs(self.voting_1.max_votes, 200)
        self.assertIs(CharacterVote.objects.all().exists(), False)
        CharacterVote.objects.create(
            voting=self.voting_1,
            character=self.character_1,
            amount=150
        )
        response = self.client.get(reverse('voting-active'))
        self.assertEqual(response.status_code, 200)
        results = response.json()['results']
        active_titles = [v['title'] for v in results]
        self.assertIn(self.voting_1.title, active_titles)
        recieved_voting = [v for v in results if v['title']
                           == self.voting_1.title][0]
        self.assertEqual(recieved_voting['leader_votes'], 150)

    @freeze_time('2023-07-09')
    def test_voting_is_limit_max_votes(self):
        self.assertIs(self.voting_1.max_votes, 200)
        self.assertIs(CharacterVote.objects.all().exists(), False)
        CharacterVote.objects.create(
            voting=self.voting_1,
            character=self.character_1,
            amount=200
        )
        response = self.client.get(reverse('voting-active'))
        self.assertEqual(response.status_code, 200)
        active_titles = [v['title'] for v in response.json()['results']]
        self.assertNotIn(self.voting_1.title, active_titles)

    @freeze_time('2023-07-09')
    def test_voting_is_limit_greater_max_votes(self):
        self.assertIs(self.voting_1.max_votes, 200)
        self.assertIs(CharacterVote.objects.all().exists(), False)
        CharacterVote.objects.create(
            voting=self.voting_1,
            character=self.character_1,
            amount=250
        )
        response = self.client.get(reverse('voting-active'))
        self.assertEqual(response.status_code, 200)
        active_titles = [v['title'] for v in response.json()['results']]
        self.assertNotIn(self.voting_1.title, active_titles)

    @freeze_time('2023-07-09')
    def test_voting_finished_list(self):
        """ Also check finish_by_date case"""
        response = self.client.get(reverse('voting-finished'))
        self.assertEqual(response.status_code, 200)
        titles = [v['title'] for v in response.json()['results']]
        self.assertNotIn([self.active_title], titles)
        self.assertNotIn(self.future_title, titles)

        now = timezone.now().date()
        self.assertGreater(now, self.voting_2.end_date)
        self.assertEqual([self.finished_title], titles)

    @freeze_time('2023-07-09')
    def test_no_finished_votings(self):
        Voting.objects.all().delete()
        response = self.client.get(reverse('voting-finished'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['results'], [])

    @freeze_time('2023-07-09')
    def test_voting_finished_by_max_votes(self):
        self.assertEqual(self.voting_1.max_votes, 200)
        self.assertIs(CharacterVote.objects.all().exists(), False)
        CharacterVote.objects.create(voting=self.voting_1,
                                     character=self.character_1, amount=200)
        response = self.client.get(reverse('voting-finished'))
        self.assertEqual(response.status_code, 200)
        results = response.json()['results']
        titles = [v['title'] for v in results]
        self.assertIn(self.voting_1.title, titles)
        recieved_voting = [v for v in results if v['title']
                           == self.voting_1.title][0]
        self.assertEqual(recieved_voting['leader_votes'], 200)

    def test_voting_detail(self):
        response = self.client.get(reverse('voting-detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        r_voting = response.json()
        self.assertEqual(
            [self.voting_1.id, self.voting_1.title, self.voting_1.start_date],
            [r_voting['id'], r_voting['title'],
             datetime.strptime(r_voting['start_date'], '%Y-%m-%d').date()]
        )

    def test_no_voting_detail(self):
        Voting.objects.all().delete()
        self.assertIs(Voting.objects.all().exists(), False)
        response = self.client.get(reverse('voting-detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 404)

    def test_voting_create_delete_no_access(self):
        response = self.client.put(reverse('voting-detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 403)

        response = self.client.delete(reverse('voting-detail',
                                      kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 403)

    def test_voting_members_no_voting(self):
        Voting.objects.all().delete()
        self.assertIs(Voting.objects.all().exists(), False)
        response = self.client.get(reverse('voting-members',
                                   kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 400)
        self.assertIsNone(response.json().get('results'))

        detail = response.json()['detail']
        self.assertEqual(detail, 'Voting id 1 does not exist')

    def test_voting_has_no_members(self):
        self.assertIs(CharacterVote.objects.all().exists(), False)
        response = self.client.get(reverse('voting-members',
                                   kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['results'], [])

        detail = response.json()['detail']
        self.assertEqual(detail, 'Voting id 1 has no members')

    def test_voting_has_members(self):
        CharacterVote.objects.create(voting=self.voting_1,
                                     character=self.character_1, amount=0)
        CharacterVote.objects.create(voting=self.voting_1,
                                     character=self.character_2, amount=0)

        response = self.client.get(reverse('voting-members',
                                   kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        r_names = [c['first_name'] for c in response.json()['results']]
        self.assertEqual(
            [self.character_1.first_name, self.character_2.first_name],
            r_names,
        )

    def test_winner_no_voting(self):
        Voting.objects.all().delete()
        self.assertIs(Voting.objects.all().exists(), False)
        response = self.client.get(reverse('voting-winner', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 400)
        detail = response.json()['detail']
        self.assertEqual(detail, 'Voting id 1 does not exist')

    @freeze_time('2023-07-09')
    def test_winner_active_voting(self):
        now = timezone.now().date()
        self.assertGreater(now, self.voting_1.start_date)
        self.assertLessEqual(now, self.voting_1.end_date)
        self.assertIs(CharacterVote.objects.all().exists(), False)
        response = self.client.get(reverse('voting-winner', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 400)
        detail = response.json()['detail']
        self.assertEqual(detail, 'Voting id 1 is still active')

    @freeze_time('2023-07-09')
    def test_winner_voting_has_no_members(self):
        now = timezone.now().date()
        self.assertGreater(now, self.voting_2.end_date)
        self.assertIs(CharacterVote.objects.all().exists(), False)
        response = self.client.get(reverse('voting-winner', kwargs={'pk': 2}))
        self.assertEqual(response.status_code, 400)
        detail = response.json()['detail']
        self.assertEqual(detail, 'Voting id 2 has no members')

    @freeze_time('2023-07-09')
    def test_winner_one_member(self):
        now = timezone.now().date()
        self.assertGreater(now, self.voting_2.end_date)
        self.assertIs(CharacterVote.objects.all().exists(), False)
        CharacterVote.objects.create(voting=self.voting_2,
                                     character=self.character_1, amount=0)
        response = self.client.get(reverse('voting-winner', kwargs={'pk': 2}))
        self.assertEqual(response.status_code, 200)
        winner = response.json()
        self.assertEqual(
            [self.character_1.id, self.character_1.first_name],
            [winner['id'], winner['first_name']]
        )

    @freeze_time('2023-07-09')
    def test_winner_two_members_equal_votes(self):
        now = timezone.now().date()
        self.assertGreater(now, self.voting_2.end_date)
        self.assertIs(CharacterVote.objects.all().exists(), False)
        CharacterVote.objects.create(voting=self.voting_2,
                                     character=self.character_1, amount=10)
        CharacterVote.objects.create(voting=self.voting_2,
                                     character=self.character_2, amount=10)
        response = self.client.get(reverse('voting-winner', kwargs={'pk': 2}))
        self.assertEqual(response.status_code, 400)
        detail = response.json()['detail']
        self.assertEqual(detail, 'Voting id 2 members have no leader')

    @freeze_time('2023-07-09')
    def test_winner_several_members_one_leader(self):
        now = timezone.now().date()
        self.assertGreater(now, self.voting_2.end_date)
        self.assertIs(CharacterVote.objects.all().exists(), False)
        CharacterVote.objects.create(voting=self.voting_2,
                                     character=self.character_1, amount=0)
        CharacterVote.objects.create(voting=self.voting_2,
                                     character=self.character_2, amount=50)
        CharacterVote.objects.create(voting=self.voting_2,
                                     character=self.character_3, amount=100)
        response = self.client.get(reverse('voting-winner', kwargs={'pk': 2}))
        self.assertEqual(response.status_code, 200)
        winner = response.json()
        self.assertEqual(
            [self.character_3.id, self.character_3.first_name],
            [winner['id'], winner['first_name']]
        )

    def test_characters_list(self):
        response = self.client.get(reverse('character-list'))
        self.assertEqual(response.status_code, 200)
        titles = [v['first_name'] for v in response.json()['results']]
        names = [self.character_1.first_name, self.character_2.first_name,
                 self.character_3.first_name]
        self.assertEqual(titles, names)

    def test_no_character_list(self):
        Character.objects.all().delete()
        response = self.client.get(reverse('character-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['results'], [])

    def test_character_detail(self):
        response = self.client.get(reverse('character-detail',
                                   kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        character = response.json()
        self.assertEqual(
            [self.character_1.id, self.character_1.first_name],
            [character['id'], character['first_name']],
        )

    def test_no_character_detail(self):
        Character.objects.all().delete()
        self.assertIs(Character.objects.all().exists(), False)
        response = self.client.get(reverse('character-detail',
                                   kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 404)

    def test_character_create_delete_no_access(self):
        response = self.client.delete(reverse('character-detail',
                                      kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 403)

        response = self.client.delete(reverse('character-detail',
                                      kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 403)

    def test_add_vote_no_voting(self):
        Voting.objects.all().delete()
        response = self.client.put(reverse('voting-add-vote',
                                   kwargs={'pk': 1, 'pk_2': 1}))
        self.assertEqual(response.status_code, 400)
        detail = response.json()['detail']
        self.assertEqual(detail, 'Voting id 1 does not exist')

    def test_add_vote_voting_finished(self):
        response = self.client.put(reverse('voting-add-vote',
                                   kwargs={'pk': 2, 'pk_2': 1}))
        self.assertEqual(response.status_code, 400)
        detail = response.json()['detail']
        self.assertEqual(detail, 'Voting id 2 is finished')

    def test_add_vote_no_member(self):
        self.assertIs(CharacterVote.objects.all().exists(), False)
        response = self.client.put(reverse('voting-add-vote',
                                   kwargs={'pk': 1, 'pk_2': 1}))
        self.assertEqual(response.status_code, 400)
        detail = response.json()['detail']
        self.assertEqual(detail, 'Voting id 1 has no member id 1')

    def test_add_vote(self):
        voting = Voting.objects.filter(id=1)\
            .prefetch_related('votes')\
            .annotate(votes_amount=Sum('votes__amount'))
        self.assertEqual(voting.get().votes_amount, None)
        CharacterVote.objects.create(
            voting=self.voting_1,
            character=self.character_1,
            amount=0
        )
        for i in range(1, 6):
            response = self.client.put(reverse('voting-add-vote',
                                       kwargs={'pk': 1, 'pk_2': 1}))
            self.assertEqual(response.status_code, 201)
            self.assertEqual(voting.get().votes_amount, i)

    def test_get_image_no_access(self):
        file_path = self.character_1.photo.path
        response = self.client.get(
            reverse('file-download',
                    kwargs={'file_path': file_path}))
        self.assertEqual(response.status_code, 403)

    def test_get_image(self):
        self.client.force_login(self.admin)
        relative_path = self.character_1.photo.name
        full_path = os.path.join(self.media_root,
                                 relative_path)
        response = self.client.get(
            reverse(
                'file-download',
                kwargs={'file_path': relative_path},
            )
        )
        r_image = io.BytesIO(b"".join(response.streaming_content)).getvalue()
        with open(full_path, 'rb') as file:
            b_image = file.read()
        self.assertEqual(b_image, r_image)

    def test_no_image(self):
        self.client.force_login(self.admin)
        file_path = self.character_3.photo.path
        self.assertIs(os.path.isfile(file_path), False)
        response = self.client.get(
            reverse('file-download',
                    kwargs={'file_path': file_path}))
        self.assertEqual(response.status_code, 400)
        detail = response.json()['detail']
        self.assertEqual(detail, f'No file {file_path}')
