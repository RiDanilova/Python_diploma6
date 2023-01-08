from django.contrib.auth import get_user_model, login, logout

from rest_framework import generics, status, permissions
from rest_framework.response import Response

from .serializers import RegistrationSerializer, LoginSerializer, ProfileSerializer, UpdatePasswordSerializer

USER_MODEL = get_user_model()


class RegistrationView(generics.CreateAPIView):
    """Класс для регистрации пользователя, использующий сериализатор из 'serializer_class'"""
    model = USER_MODEL
    serializer_class = RegistrationSerializer


class LoginView(generics.GenericAPIView):
    """Класс для входа пользователя, использующий сериализатор из 'serializer_class',
        проверяющий валидность введенных данных"""
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        """Использование сериализатора для проверки входных данных"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        login(request=request, user=user)

        return Response(serializer.data)


class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    """Класс для просмотра профиля пользователя, использующий сериализатор из 'serializer_class',
        модель 'USER_MODEL' и выданные разрешения (permission_classes)"""
    serializer_class = ProfileSerializer
    queryset = USER_MODEL.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Получение сведений о профиле пользователя"""
        return self.request.user

    def delete(self, request, *args, **kwargs):
        """Выход из профиля пользователя"""
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UpdatePasswordView(generics.UpdateAPIView):
    """Класс для изменения текущего пароля на новый,
        использующий сериализатор из 'serializer_class' и выданные разрешения (permission_classes)"""
    serializer_class = UpdatePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
