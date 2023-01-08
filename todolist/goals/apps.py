from django.apps import AppConfig

VERBOSE_APP_NAME = "Список досок, категорий и целей"


class GoalsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "goals"
    verbose_name = VERBOSE_APP_NAME
