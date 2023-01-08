from django.contrib import admin

from goals.models import GoalCategory, Board, GoalComment, Goal

admin.site.site_header = "Модуль 7 SkyPro"
admin.site.site_title = "Диплом"
admin.site.index_title = "TodoList"


class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created", "updated")
    search_fields = ("title", "user")


admin.site.register(GoalCategory, GoalCategoryAdmin)
admin.site.register(Goal)
admin.site.register(GoalComment)
admin.site.register(Board)
