from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, filters, generics
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.pagination import LimitOffsetPagination

from goals.filters import GoalDateFilter
from goals.models import GoalCategory, Goal, GoalComment, Board
from goals.permissions import BoardPermissions, CommentPermissions, CategoryPermissions, GoalPermissions
from goals.serializers import GoalCreateSerializer, GoalCategorySerializer, GoalCategoryCreateSerializer, \
    GoalSerializer, GoalCommentCreateSerializer, GoalCommentSerializer, BoardCreateSerializer, BoardSerializer, \
    BoardListSerializer


class GoalCategoryCreateView(generics.CreateAPIView):
    """Класс создания категорий, с использованием модели категорий (model),
        выданных разрешений (permission_classes) и сериализатора (serializer_class)"""
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategoryCreateSerializer


class GoalCategoryListView(generics.ListAPIView):
    """Класс отображения списка категорий, с использованием модели категорий (model),
        выданных разрешений (permission_classes), сериализатора (serializer_class), пагинатора (pagination_class) и
        фильтров (filter_backends)"""
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["board", "user"]  # Поля, по которым производится фильтрация категорий (доска и автор)
    ordering_fields = ["title", "created"]  # Поля, по которым производится сортировка категорий (название и дата создания)
    ordering = ["title"]  # Сортировка категорий (по названию)
    search_fields = ["title"]  # Поле, по которому производится поиск категорий (по названию)

    def get_queryset(self):
        """Переопределенное значение при использовании фильтров для поиска значений"""
        return GoalCategory.objects.filter(board__participants__user=self.request.user, is_deleted=False)


class GoalCategoryView(generics.RetrieveUpdateDestroyAPIView):
    """Класс отображения/изменения/удаления списка категорий, с использованием модели категорий (model),
        выданных разрешений (permission_classes) и сериализатора (serializer_class)"""
    model = GoalCategory
    serializer_class = GoalCategorySerializer
    permission_classes = [permissions.IsAuthenticated, CategoryPermissions]

    def get_queryset(self):
        """Переопределенное значение при использовании фильтров для поиска значений"""
        return GoalCategory.objects.filter(board__participants__user=self.request.user, is_deleted=False)

    def perform_destroy(self, instance):
        """Удаление экземпляра объекта - Категории"""
        with transaction.atomic():
            instance.is_deleted = True
            instance.save()
            Goal.objects.filter(board__participants__user=self.request.user, is_deleted=False)
        return instance


class GoalCreateView(generics.CreateAPIView):
    """Класс создания целей, с использованием модели целей (model),
        выданных разрешений (permission_classes) и сериализатора (serializer_class)"""
    model = Goal
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCreateSerializer


class GoalListView(generics.ListAPIView):
    """Класс отображения списка целей, с использованием модели целей (model),
        выданных разрешений (permission_classes), сериализатора (serializer_class), пагинатора (pagination_class) и
        фильтров (filter_backends)"""
    model = Goal
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_class = GoalDateFilter  # Фильтр, определенный в файле 'filters.py'
    ordering_fields = ["due_date", "priority"]  # Поля, по которым производится сортировка (дата дедлайна и приоритет)
    ordering = ["priority", "due_date"]  # Сортировка целей (по дате дедлайна и приоритету)
    search_fields = ["title", "description"]  # Поля, по которым производится поиск целей (по названию и описанию)

    def get_queryset(self):
        """Переопределенное значение при использовании фильтров для поиска значений"""
        return Goal.objects.filter(category__board__participants__user=self.request.user)


class GoalView(generics.RetrieveUpdateDestroyAPIView):
    """Класс отображения/изменения/удаления списка целей, с использованием модели целей (model),
        выданных разрешений (permission_classes) и сериализатора (serializer_class)"""
    model = Goal
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated, GoalPermissions]

    def get_queryset(self):
        """Переопределенное значение при использовании фильтров для поиска значений"""
        return Goal.objects.filter(category__board__participants__user=self.request.user)

    def perform_destroy(self, instance):
        """Удаление экземпляра объекта (целей). В данном случае - его архивация"""
        instance.status = Goal.Status.archived
        instance.save()
        return instance


class GoalCommentCreateView(generics.CreateAPIView):
    """Класс создания комментариев к целям, с использованием модели комментариев (model),
        выданных разрешений (permission_classes) и сериализатора (serializer_class)"""
    model = GoalComment
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentCreateSerializer

    def perform_create(self, serializer: GoalCommentCreateSerializer):
        """Для сохранения нового экземпляра объекта (комментария)"""
        serializer.save(goal_id=self.request.data["goal"])


class GoalCommentListView(generics.ListAPIView):
    """Класс отображения списка комментариев к целям, с использованием модели комментариев (model),
        выданных разрешений (permission_classes), сериализатора (serializer_class),
        пагинатора (pagination_class) и фильтров (filter_backends)"""
    model = GoalComment
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ["goal"]  # Поля, по которым производится сортировка
    ordering = ["-created"]  # Сортировка по дате создания комментария (последние комментарии - вверху)

    def get_queryset(self):
        """Переопределенное значение при использовании фильтров для поиска значений"""
        return GoalComment.objects.filter(goal__category__board__participants__user=self.request.user)


class GoalCommentView(generics.RetrieveUpdateDestroyAPIView):
    """Класс отображения/изменения/удаления списка комментариев к целям,
        с использованием модели комментариев (model), выданных разрешений (permission_classes)
        и сериализатора (serializer_class)"""
    model = GoalComment
    permission_classes = [permissions.IsAuthenticated, CommentPermissions]
    serializer_class = GoalCommentSerializer

    def get_queryset(self):
        """Переопределенное значение при использовании фильтров для поиска значений"""
        return GoalComment.objects.filter(goal__category__board__participants__user=self.request.user)


# Board's views
class BoardCreateView(CreateAPIView):
    """Класс создания досок, с использованием модели досок (model),
        выданных разрешений (permission_classes) и сериализатора (serializer_class)"""
    model = Board
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BoardCreateSerializer


class BoardListView(ListAPIView):
    """Класс отображения списка досок, с использованием модели досок (model),
        выданных разрешений (permission_classes), сериализатора (serializer_class),
        пагинатора (pagination_class) и фильтров (filter_backends)"""
    model = Board
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LimitOffsetPagination
    serializer_class = BoardListSerializer
    filter_backends = [filters.OrderingFilter]
    ordering = ["title"]  # Сортировка по названию доски

    def get_queryset(self):
        """Переопределенное значение при использовании фильтров для поиска значений"""
        return Board.objects.filter(participants__user=self.request.user, is_deleted=False)


class BoardView(RetrieveUpdateDestroyAPIView):
    """Класс отображения/изменения/удаления списка досок,
        с использованием модели досок (model), выданных разрешений (permission_classes)
        и сериализатора (serializer_class)"""
    model = Board
    permission_classes = [permissions.IsAuthenticated, BoardPermissions]
    serializer_class = BoardSerializer

    def get_queryset(self):
        """Переопределенное значение при использовании фильтров для поиска значений"""
        return Board.objects.filter(participants__user=self.request.user, is_deleted=False)

    def perform_destroy(self, instance: Board):
        """Удаление экземпляра объекта. В данном случае: удаление доски и архивация целей"""
        with transaction.atomic():
            instance.is_deleted = True
            instance.save()
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=instance).update(status=Goal.Status.archived)
        return instance
