from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User

admin.site.site_header = "Модуль 7 SkyPro"
admin.site.site_title = "Диплом"
admin.site.index_title = "TodoList"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "first_name", "last_name")  # Отображение полей в Админке
    search_fields = ("email", "first_name", "last_name", "username")  # Поиск по полям в Админке
    list_filter = ("is_staff", "is_active", "is_superuser")  # Фильтры по полям в Админке
    exclude = ('password',)  # Скрываем поле "Пароль" в Админке
    readonly_fields = ("last_login", "date_joined")  # Поля только для чтения в Админке
