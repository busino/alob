'''
Alob Project
2017 
Author(s): R. Walker
'''
from django import forms

from .models import Prediction


class PredictionForm(forms.ModelForm):

    class Meta:
        model = Prediction
        fields = ('name', 'pools')
        widgets = {
            'pools': forms.SelectMultiple(attrs={'size': 24}),
        }