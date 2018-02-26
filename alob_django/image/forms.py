'''
Alob Project
2017
Author(s): R.Walker

'''
from django import forms

from .models import ImagePool, Image


class ImageForm(forms.ModelForm):
    
    pools = forms.ModelMultipleChoiceField(queryset=ImagePool.objects.order_by('-id'), 
                                           label=('Pools'),
                                           required=False)
    comment = forms.CharField(required=False, widget=forms.Textarea({'cols': '40', 'rows': '2'}))
    
    class Meta:
        model = Image
        fields = ('name', 'image', 
                  'project', 'date', 'location', 
                  'juvenile', 'has_eggs', 
                  'operator', 'quality', 'disabled', 'comment',
                  'pools')