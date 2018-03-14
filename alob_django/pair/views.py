'''
Alob Project
2016 - 2018
Author(s): R.Walker

'''
from time import clock
import datetime
import json
import os
import io

import numpy
from skimage.transform._geometric import matrix_transform

from django.views import generic
from django.shortcuts import render, redirect, render_to_response
from django.conf import settings
from django.http.response import HttpResponse
from django import forms
from django.forms.forms import Form
from django.urls.base import reverse_lazy
from django_filters.views import FilterView
from django.core.files.base import ContentFile

from alob_plot.pair import pair_plot
from alob.match import match_pc, match_images

from .models import Pair
from .filter import PairFilter

DEFAULT_PAGINATION_BY = 100
DEFAULT_PAGINATE_ORPHANS = 10

APP_NAME = 'pair'
APP_CLASS = Pair


class IndexView(generic.ListView):
  
    template_name = '{}/index.html'.format(APP_NAME)
    paginate_orphans = DEFAULT_PAGINATE_ORPHANS
    paginate_by = DEFAULT_PAGINATION_BY

    def get_queryset(self):
        return Pair.objects\
                   .prefetch_related('first', 'second', 'first__points', 'second__points')\
                   .all()\
                   .order_by('-match')


class DetailView(generic.DetailView):
  
    model = APP_CLASS
    template_name = '{}/detail.html'.format(APP_NAME)

    def get_queryset(self):
        return Pair.objects\
                   .prefetch_related('first', 'second')\
                   .all()

    def get_context_data(self, **kwargs):

        context = super(DetailView, self).get_context_data(**kwargs)
        pair = kwargs['object']

        search_radius = float(self.request.GET.get('search_radius', settings.SEARCH_RADIUS))

        if pair.first.is_labeled and pair.second.is_labeled:
            
            src = pair.first.pc_recarr()
            dst = pair.second.pc_recarr()
            
            src_coords = numpy.array([src['x'], src['y']])
            dst_coords = numpy.array([dst['x'], dst['y']])
    
            src_ref_points, src_warts = src_coords[:,:4], src_coords[:,4:]
            dst_ref_points, dst_warts = dst_coords[:,:4], dst_coords[:,4:]
            
            t1 = clock()
            _, _, num_matches = match_pc(src_warts,
                                         dst_warts,
                                         search_radius)

            dst_corrected, (src_matching_points, dst_matching_points), transform, _, calc_num_matches = match_images(src_warts, dst_warts, search_radius)


            dst_ref_points_corrected = matrix_transform(dst_ref_points.T, transform).T

            result = calc_num_matches/min(src_warts.shape[1], dst_warts.shape[1])
            time_used = clock()-t1

            # Create the plot
            context['plot_js'], context['plot_div'] = pair_plot(src_warts, dst_corrected,
                                                                src_matching_points, dst_matching_points,
                                                                src_ref_points, dst_ref_points_corrected,
                                                                dst_warts, dst_ref_points,
                                                                circle_radius=search_radius/2,
                                                                plot_width=800, plot_height=600, create_components=True)
        else:
            result = 0
            transform = 0
            time_used = 0

        # evaluate some data
        context['diff_num_points'] = abs(pair.first.num_points - pair.second.num_points)
        context['matches'] = num_matches
        context['calc_matches'] = calc_num_matches
        context['result'] = result
        context['search_radius'] = search_radius
        context['time_used'] = time_used
        context['transform'] = transform
        return context


class FilterView(FilterView):
    
    filterset_class = PairFilter
    
    template_name = '{}/filter.html'.format(APP_NAME)

    def get(self, request, *args, **kwargs):
        
        filterset_class = self.get_filterset_class()
        self.filterset = self.get_filterset(filterset_class)
        self.object_list = self.filterset.qs
        # Do not select to much entries!!!
        if not request.GET.keys():
            self.object_list = APP_CLASS.objects.none()

        if self.object_list.count() > 2000:
            self.object_list = self.object_list[:2000]
        context = self.get_context_data(filter=self.filterset,
                                        object_list=self.object_list)
        '''
        if 'excel' in request.GET.keys():
            output = export_images_excel(context['object_list'])
            response = HttpResponse(output, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", charset='utf-8')
            response['Content-Disposition'] = "attachment; filename=Images.xlsx"
            return response
        elif 'csv' in request.GET.keys():
            output = export_images_csv(context['object_list'])
            response = StreamingHttpResponse(output,
                                             content_type="text/csv")
            response['Content-Disposition'] = 'attachment; filename="Images.csv"'
            return response
        elif 'pool' in request.GET.keys():
            p = ImagePool.objects.create(name=request.GET.get('pool_name', 'MyPool'))
            p.images.set(context['object_list'])
            return HttpResponseRedirect(redirect_to=reverse_lazy('image:pool:detail', kwargs={'pk': p.pk}))
        '''
        return self.render_to_response(context)

class ExportCSV(generic.ListView):

    
    def get(self, request, *args, **kwargs):


        from django.db import connection

        columns = ['pk', 'match', 'comment', 'first_id', 'first__name', 'second_id', 'second__name']
        p_query = Pair.objects.all().values_list(*columns).order_by('-match')

        #
        # CSV
        #
        header = ';'.join(columns) + '\n'
        out_str = ('{};'*len(columns))[:-1] + '\n'
        
        io = io.StringIO()
        io.write(header)
        with connection.cursor() as cursor:
            cursor.execute('{}'.format(p_query.query))
            [io.write(out_str.format(*v)) for v in cursor.fetchall()]
        
        cf = ContentFile(io.getvalue())
        response = HttpResponse(cf,
                                content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="Pairs.csv"'
        return response            


def update(request, pk):
    
    match = request.GET.get('match', None)
    if match is not None:
        match = {'0': 0, '1': 1, '-1': -1}[match]
    updated = Pair.objects.filter(pk=pk).update(match=match)
    data = dict(success=True, match=match)
    return HttpResponse(json.dumps(data), content_type='application/json')


def comment(request, pk):
    
    comment = request.POST.get('comment', '')
    Pair.objects.filter(pk=pk).update(comment=comment)
    return redirect(reverse_lazy('pair:detail', kwargs={'pk': pk}))


