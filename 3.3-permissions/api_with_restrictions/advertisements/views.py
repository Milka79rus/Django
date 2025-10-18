from django.db import models
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.exceptions import PermissionDenied

from advertisements.models import Advertisement, AdvertisementStatusChoices
from advertisements.serializers import AdvertisementSerializer
from advertisements.filters import AdvertisementFilter


class AdvertisementViewSet(ModelViewSet):
    """ViewSet для объявлений."""

    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = AdvertisementFilter
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def get_permissions(self):
        """Права доступа для действий."""
        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
            "add_to_favorites",
            "remove_from_favorites",
        ]:
            return [IsAuthenticated()]
        return []

    def get_queryset(self):
        user = self.request.user
        qs = Advertisement.objects.all()

        # Показываем черновики только автору
        if user.is_authenticated:
            qs = qs.filter(
                models.Q(
                    status__in=[
                        AdvertisementStatusChoices.OPEN,
                        AdvertisementStatusChoices.CLOSED,
                    ]
                )
                | models.Q(status=AdvertisementStatusChoices.DRAFT, creator=user)
            )
        else:
            qs = qs.exclude(status=AdvertisementStatusChoices.DRAFT)

        # Фильтр по избранным (?favorite=true)
        favorite = self.request.query_params.get("favorite")
        if favorite and favorite.lower() == "true" and user.is_authenticated:
            qs = qs.filter(favorited_by=user)

        return qs

    def perform_create(self, serializer):
        """Создание объявления с проверкой лимита открытых."""
        user = self.request.user
        open_ads = Advertisement.objects.filter(creator=user, status="OPEN").count()
        if open_ads >= 10:
            raise PermissionDenied("У вас уже есть 10 открытых объявлений.")
        serializer.save(creator=user)

    def perform_destroy(self, instance):
        """Удалять может только автор или админ."""
        user = self.request.user
        if instance.creator != user and not user.is_staff:
            raise PermissionDenied("Вы не можете удалять чужие объявления.")
        instance.delete()

    def perform_update(self, serializer):
        """Редактировать может только автор или админ."""
        user = self.request.user
        if serializer.instance.creator != user and not user.is_staff:
            raise PermissionDenied("Вы не можете редактировать чужие объявления.")
        serializer.save()

    # Добавляем действия для избранного
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def add_to_favorites(self, request, pk=None):
        ad = self.get_object()
        user = request.user
        if ad.creator == user:
            return Response(
                {"detail": "Нельзя добавить своё объявление в избранное."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ad.favorited_by.add(user)
        return Response(
            {"detail": "Объявление добавлено в избранное."}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def remove_from_favorites(self, request, pk=None):
        ad = self.get_object()
        user = request.user
        ad.favorited_by.remove(user)
        return Response(
            {"detail": "Объявление удалено из избранного."}, status=status.HTTP_200_OK
        )
