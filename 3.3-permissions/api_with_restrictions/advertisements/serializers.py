from django.contrib.auth.models import User
from rest_framework import serializers

from advertisements.models import Advertisement, AdvertisementStatusChoices


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
        )


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )
    favorited_by = UserSerializer(read_only=True, many=True)

    class Meta:
        model = Advertisement
        fields = (
            "id",
            "title",
            "description",
            "creator",
            "status",
            "created_at",
            "favorited_by",
        )

    def create(self, validated_data):
        """Метод для создания"""

        # Простановка значения поля создатель по-умолчанию.
        # Текущий пользователь является создателем объявления
        # изменить или переопределить его через API нельзя.
        # обратите внимание на `context` – он выставляется автоматически
        # через методы ViewSet.
        # само поле при этом объявляется как `read_only=True`
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Проверяем лимит открытых объявлений."""

        request = self.context.get("request")
        user = getattr(request, "user", None)

        # Проверяем только для авторизованных пользователей
        if not user or not user.is_authenticated:
            return data

        # Определяем статус, который будет у объявления после сохранения
        new_status = data.get("status")
        instance = getattr(self, "instance", None)

        if instance is None:
            # Создание объявления
            will_be_open = (
                new_status or AdvertisementStatusChoices.OPEN
            ) == AdvertisementStatusChoices.OPEN
        else:
            # Обновление объявления
            will_be_open = (
                new_status or instance.status
            ) == AdvertisementStatusChoices.OPEN

        if will_be_open:
            # Получаем количество открытых объявлений пользователя (исключая текущее, если обновление)
            qs = Advertisement.objects.filter(
                creator=user, status=AdvertisementStatusChoices.OPEN
            )
            if instance is not None:
                qs = qs.exclude(pk=instance.pk)

            if qs.count() >= 10:
                raise serializers.ValidationError(
                    "Нельзя иметь больше 10 открытых объявлений."
                )

        return data
