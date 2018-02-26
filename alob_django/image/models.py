'''
 Alob Project
 2016
 Author(s): R. Walker
'''
import os
import logging
from itertools import combinations
import cmath

from django.db import models
from django.db.models import Q
from django.utils.functional import cached_property

import numpy
import PIL, PIL.ImageDraw
import pandas

from alob_plot.colors import *
from alob.utils import norm, rot


log = logging.getLogger('alob')

BB = 36
MARK_COLOR = [255, 0, 0]

COORD_TYPE_CHOICES = ['local', 'geo']


class Image(models.Model):
    
    project = models.CharField(max_length=48, blank=True, null=True)
    name = models.CharField(max_length=64, unique=True)
    date = models.DateField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=64, blank=True, null=True, default=None)
    juvenile = models.NullBooleanField(default=None)
    operator = models.CharField(max_length=4, blank=True, null=True, default=None)
    quality = models.PositiveSmallIntegerField(choices=[(0, 'bad'),(1, 'good'),(2, 'perfect')], default=1)
    has_eggs = models.NullBooleanField(default=None)
    image = models.FileField(null=True, blank=True)
    disabled = models.BooleanField(default=False)
    comment = models.TextField(max_length=240, default='', blank=True, null=True)

    coord_type = models.CharField(max_length=16, default='geo', choices=[(v,v) for v in COORD_TYPE_CHOICES])
    is_labeled = models.BooleanField(default=False)

    class Meta:
        app_label = 'image'
        db_table = 'image'
        ordering = ('location', '-date', 'disabled', 'quality')        

    def __unicode__(self):
        return '%s(id=%s, name=%s, date=%s)' % (self.__class__.__name__, self.id, self.name, self.date)

    def __str__(self):
        return self.__unicode__()

    @cached_property
    def num_points(self):
        return self.points.count()-4

    def point_cloud(self):
        return numpy.array([(p.x, p.y) for p in self.points.all()]).T

    def c_point_cloud(self):
        return numpy.array([p.x + p.y*1j for p in self.points.all()]).T

    def pc_df(self):
        df = pandas.DataFrame(list(self.points.values('pk', 'id', 'x', 'y', 'type'))).set_index('pk')
        df['pos'] = df.x + 1j*df.y
        return df

    def new_point_cloud(self):
        df = self.pc_df()
        tail = df[df.type=='tail'].pos.values[0]
        right_eye = df[df.type=='right_eye'].pos.values[0]
        left_eye = df[df.type=='left_eye'].pos.values[0]
        nose = df[df.type=='nose'].pos.values[0]
        
        # origin = (right_eye+left_eye)/2
        origin = (right_eye+left_eye)/2
        dir_x = norm(tail-nose)
        scale_factor = abs(origin-right_eye)
        # Translate Points, Rotate and Scale
        df.pos = rot(df.pos - origin, -cmath.phase(dir_x))/scale_factor
        df.x, df.y = df.pos.real, df.pos.imag
        return df

    def pc_recarr(self):
        fields = ['x', 'y', 'type', 'id']
        arr = numpy.core.records.array(list(self.points.values_list(*fields)), names=fields)
        tail = arr[arr['type']=='tail'][0]
        right_eye = arr[arr['type']=='right_eye'][0]
        left_eye = arr[arr['type']=='left_eye'][0]
        nose = arr[arr['type']=='nose'][0]
        
        left_eye, right_eye = left_eye['x']+1j*left_eye['y'], right_eye['x']+1j*right_eye['y']
        tail, nose = tail['x']+1j*tail['y'], nose['x']+1j*nose['y']
        
        # origin = (right_eye+left_eye)/2
        origin = (right_eye+left_eye)/2
        dir_x = norm(tail-nose)
        scale_factor = abs(origin-right_eye)
        # Translate Points, Rotate and Scale
        arr_c = arr['x'] + 1j*arr['y']
        arr_c_t = rot(arr_c - origin, -cmath.phase(dir_x))/scale_factor
        arr['x'], arr['y'] = arr_c_t.real, arr_c_t.imag
        return arr
        
    def img(self, crop=False):
        if self.image:
            img = PIL.Image.open(self.image.path).convert('RGBA')
            x_min, x_max = 0, 0
            if crop and self.points.exists():
                pc = self.point_cloud()
                X_OFFSET = 200
                Y_OFFSET = 360
                x_min, x_max = pc[0].min()-X_OFFSET, pc[0].max()+X_OFFSET
                y_min, y_max = pc[1].min()-Y_OFFSET, pc[1].max()+Y_OFFSET
                y_min_pil, y_max_pil = img.size[1]-y_max, img.size[1]-y_min
                img = img.crop([x_min, y_min_pil, x_max, y_max_pil])
                return img, x_min, y_min
            return img, x_min, x_max
        return None, 0, 0
    
    @cached_property
    def jpeg_file(self):
        if self.image:
            return self.image.path
        return None

    def marked_image(self, crop=False, mark=True):
        if self.image:
            img, x_min, y_min = self.img(crop=crop)
            dr = PIL.ImageDraw.Draw(img)
            pxs, pys = [], []
            for p in self.points.all():
                px = p.x - x_min
                py = img.size[1] - (p.y - y_min)
                if mark:
                    #poly_r, poly_c = [px-BB, px+BB, px+BB, px-BB], [py-BB, py-BB, py+BB, py+BB]
                    #img[skimage.draw.polygon_perimeter(poly_r, poly_c, shape=img.shape)] = MARK_COLOR
                    #poly_r, poly_c = [px-BB+1, px+BB-1, px+BB-1, px-BB+1], [py-BB+1, py-BB+1, py+BB-1, py+BB-1]
                    #img[skimage.draw.polygon_perimeter(poly_r, poly_c, shape=img.shape)] = MARK_COLOR
                    #dr.polygon([px-BB, py-BB, px+BB, py-BB, px+BB, py+BB, px-BB, py+BB], outline='red')
                    color = type2color(p.type)
                    dr.line([px-BB, py, px+BB, py], fill=color, width=2)
                    dr.line([px, py-BB, px, py+BB], fill=color, width=2)
                    dr.ellipse([px-BB, py-BB, px+BB, py+BB], outline=color)
                pxs.append(px), pys.append(py)
            #if crop:
            #    # crop the image to fit back
            #    min_x, min_y = round(min(pxs)*0.75), round(min(pys)*0.75)
            #    max_x, max_y = round(max(pxs)*1.25), round(max(pys)*1.25)
            #    img = img[min_x:max_x, min_y:max_y]
            return img
        return None


class ImagePool(models.Model):
    
    name = models.CharField(max_length=64, unique=True)
    images = models.ManyToManyField(to='image.Image', related_name='pools')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'image'
        db_table = 'image_pool'
    
    def __unicode__(self):
        return '{}(id={}, name={}, created={}, num_images={})'.format(self.__class__.__name__, 
                                                                      self.id, self.name, 
                                                                      self.created,
                                                                      self.images.count())

    def __str__(self):
        return self.__unicode__()
    
    def generate_pairs(self):
        
        from pair.models import Pair
        
        images = Image.objects.filter(pools=self)
        image_combinations = combinations(images, 2)
        to_generate = []
        for first, second in image_combinations:
            if not Pair.objects.filter((Q(first=first) & Q(second=second)) | 
                                   (Q(first=second) & Q(second=first))).exists():
                to_generate.append(first, second)
                
        log.info('Generate {} pairs.'.format(len(to_generate)))
        r = Pair.objects.bulk_create([Pair(first=first, second=second) for first, second in to_generate])
        log.info(r)

    @cached_property
    def pairs(self):
        from pair.models import Pair
        return Pair.objects.filter(first__pools=self, second__pools=self).distinct()


POINT_TYPE_CHOICES = ['wart', 'nose', 'tail', 'left_eye', 'right_eye']


class Point(models.Model):
    
    image = models.ForeignKey(Image, related_name='points', null=True)
    x = models.FloatField(null=True)
    y = models.FloatField(null=True)
    type = models.CharField(max_length=16, default='wart', choices=[(v, v) for v in POINT_TYPE_CHOICES])

    class Meta:
        app_label = 'image'
        db_table = 'point'
        ordering = ['image_id', 'type']

    def __unicode__(self):
        return '{}(id={}, type={} pos=({}, {}))'.format(self.__class__.__name__, self.id, self.type, self.x, self.y)

    def __str__(self):
        return self.__unicode__()
