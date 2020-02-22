'''
Alob Project
2016 - 2018
Author(s): R.Walker

'''
import django_filters

from .models import Image


class ImageFilter(django_filters.FilterSet):

    name = django_filters.CharFilter(lookup_expr='icontains')
    date = django_filters.DateFilter()
    created_gte = django_filters.DateFilter(field_name='created', label='Created >=', lookup_expr='gte')
    created_lt = django_filters.DateFilter(field_name='created', label='Created <', lookup_expr='lt')
    location = django_filters.CharFilter(lookup_expr='icontains')
    comment = django_filters.CharFilter(lookup_expr='icontains')
    pools__name = django_filters.CharFilter(lookup_expr='icontains')


    class Meta:
        model = Image
        fields = ['id', 'project', 'name', 
                  'date', 'location', 
                  'juvenile', 'has_eggs',
                  'quality', 'is_labeled', 'coord_type', 'created_gte', 'created_lt',
                  'disabled', 'comment', 'pools__name'] #, 'pools']

