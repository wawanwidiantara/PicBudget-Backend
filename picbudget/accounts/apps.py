from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "picbudget.accounts"

    def ready(self):
        import picbudget.accounts.signals
