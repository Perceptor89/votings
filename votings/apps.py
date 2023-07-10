from django.apps import AppConfig


class VotingsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "votings"

    def ready(self):
        import votings.signals
