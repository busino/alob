'''
 Alob Project
 
 Author(s): R. Walker
'''
from django.db import models
import numpy
from alob.ml.classifier import AlobPairClassifier


class Pair(models.Model):
    
    first = models.ForeignKey('image.Image', related_name='firsts', related_query_name='first', null=True)
    second = models.ForeignKey('image.Image', related_name='seconds', related_query_name='second', null=True)
    result = models.FloatField(null=True, default=0.)
    match = models.SmallIntegerField(choices=[(0, 'No Match'), (1, 'Match'), (-1, 'Undefined'), (None, 'Not Set')], default=None, null=True)#models.NullBooleanField(default=None)
    rot = models.FloatField(default=0.)
    t_x = models.FloatField(default=0.)
    t_y = models.FloatField(default=0.)
    scale_x = models.FloatField(default=0.)
    scale_y = models.FloatField(default=0.)
    shear = models.FloatField(default=0.)
    comment = models.TextField(max_length=240, default='')
    disabled_for_training = models.BooleanField(default=False)
    #images = models.ManyToManyField(to='image.Image', related_name='pairs')

    class Meta:
        app_label = 'pair'
        db_table = 'pair'
        ordering = ('first_id', '-result', 'second_id')
        unique_together = (('first', 'second'),)

    def __unicode__(self):
        return '%s(id=%s, first=%s, second=%s)' % (self.__class__.__name__, self.id, self.first, self.second)

    def __str__(self):
        return self.__unicode__()

    def features(self):
        from django.conf import settings
        images = [self.first.pc_recarr(), self.second.pc_recarr()]
        pairs = numpy.array([[0,1]])
        c = AlobPairClassifier(settings.SEARCH_RADIUS)
        f = c.extract_features(images, pairs)
        return f[0]


class PairPool(models.Model):
    
    name = models.CharField(max_length=64)
    pairs = models.ManyToManyField(to=Pair, related_name='pools')

    class Meta:
        app_label = 'pair'
        db_table = 'pair_pool'
    
    def __unicode__(self):
        return '{}(id={}, name={}, num_pairs={})'.format(self.__class__.__name__, self.id, self.name, self.pairs.count())

    def __str__(self):
        return self.__unicode__()
