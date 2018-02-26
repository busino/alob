'''
 Alob Project
 2017
 Author(s): R. Walker
'''
import django_filters

from .models import Pair


class PairFilter(django_filters.FilterSet):

    first__name = django_filters.CharFilter(lookup_expr='icontains')
    second__name = django_filters.CharFilter(lookup_expr='icontains')
    comment = django_filters.CharFilter(lookup_expr='icontains')
    pools__name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Pair
        fields = ['id', 'first__name', 'second__name', 'match', 'comment', 'pools__name']

    @property
    def qs(self):
        qs = super(PairFilter, self).qs
        return qs.select_related('first', 'second')