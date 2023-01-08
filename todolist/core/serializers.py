from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

USER_MODEL = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя с помощью пароля"""
    password = serializers.CharField(write_only=True)
    password_repeat = serializers.CharField(write_only=True)

    def validate(self, data_password):
        """Функция проверки паролей на идентичность"""
        password = data_password.get("password")
        password_repeat = data_password.pop("password_repeat")

        try:
            validate_password(password)
        except Exception as e:
            raise serializers.ValidationError({"password": e.messages})

        if password != password_repeat:
            raise serializers.ValidationError("Пароли не совпадают!")
        return data_password

    def create(self, validated_data):
        """Функция создания и хэширования пароля"""
        password = validated_data.get("password")

        validated_data["password"] = make_password(password)
        instance = super().create(validated_data)
        return instance

    class Meta:
        model = USER_MODEL
        fields = "__all__"


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def create(self, validated_data):
        """Функция создания пользователя с использованием имени 'username' и пароля 'password',
            если введенные данные были верны (имя и пароль)"""
        user = authenticate(
            username=validated_data["username"],
            password=validated_data["password"],
        )
        if not user:
            raise AuthenticationFailed
        return user

    class Meta:
        model = USER_MODEL
        fields = "__all__"


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = USER_MODEL
        fields = ("id", "username", "first_name", "last_name", "email")


class UpdatePasswordSerializer(serializers.Serializer):
    """Класс для изменения текущего пароля на новый"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        """Функция проверки корректности введенного текущего пароля.
            Если пароль введен неверно - ошибка, в противном случае - применяется новый введеный пароль"""
        user = data["user"]
        if not user.check_password(data["old_password"]):
            raise serializers.ValidationError({"old_password": "Введен неверный пароль!"})

        try:
            validate_password(data["new_password"])
        except Exception as e:
            raise serializers.ValidationError({"new_password": e.messages})

        return data

    def update(self, instance, validated_data):
        """Функция обновления и хэширования нового пароля"""
        instance.password = make_password(validated_data["new_password"])
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = USER_MODEL
        fields = ("id", "username", "first_name", "last_name", "email")
