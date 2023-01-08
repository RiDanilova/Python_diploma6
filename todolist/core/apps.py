from django.apps import AppConfig

VERBOSE_APP_NAME = "Список пользователей"


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = VERBOSE_APP_NAME
