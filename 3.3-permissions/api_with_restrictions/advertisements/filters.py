from django_filters import rest_framework as filters

from advertisements.models import Advertisement


class AdvertisementFilter(filters.FilterSet):
    """Фильтры для объявлений."""

    # Фильтр по дате создания (можно задавать диапазон)
    created_at = filters.DateFromToRangeFilter()
    favorited = filters.BooleanFilter(method="filter_favorited")

    class Meta:
        model = Advertisement
        fields = ["creator", "status", "created_at"]

    def filter_favorited(self, queryset, name, value):
        """Фильтр по избранным объявлениям."""
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorited_by=user)
        return queryset
