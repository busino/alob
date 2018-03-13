'''
Alob Project
2016 - 2018
Author(s): R.Walker

'''
from django import forms

from ..models import ImagePool, Image


class ImagePoolForm(forms.ModelForm):

    images = forms.ModelMultipleChoiceField(queryset=Image.objects, required=False,
                                            widget=forms.SelectMultiple(attrs={'size': 24, 'is_required': False}))

    class Meta:
        model = ImagePool
        fields = ('name', 'images')
