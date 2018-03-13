'''
Alob Project
2016 - 2018
Author(s): R.Walker

'''
import json

from django.db import models
from django.core.validators import validate_comma_separated_integer_list

from .apps import PredictionConfig


APP_LABEL = PredictionConfig.name

class Prediction(models.Model):
    
    name = models.CharField(max_length=124, default='', null=False)
    pools = models.ManyToManyField(to='image.ImagePool', related_name='predictions')
    status = models.CharField(max_length=12, default='created', choices=[(v,v) for v in ['created', 'running', 'failed', 'stopped', 'finished']])
    created = models.DateTimeField(auto_now_add=True)
    started = models.DateTimeField(null=True, default=None)
    ended = models.DateTimeField(null=True, default=None)
    prediction = models.CharField(max_length=9600, validators=[validate_comma_separated_integer_list])
    num_combinations = models.PositiveIntegerField(null=True)
    num_selected = models.PositiveIntegerField(null=True)
    pid = models.PositiveIntegerField(null=True, default=None)

    class Meta:
        app_label = APP_LABEL
        db_table = APP_LABEL
        ordering = ('-created',)

    def __unicode__(self):
        return '{}(id={}, name={}, status={}, created={})'.format(self.__class__.__name__, 
                                                                  self.id,
                                                                  self.name, 
                                                                  self.status, 
                                                                  self.created)

    def __str__(self):
        return self.__unicode__()

    @property
    def num_predictions(self):
        if self.prediction:
            return len(json.loads(self.prediction))
        return None