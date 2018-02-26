'''
Alob Project
2016
Author(s): R.Walker

'''
import datetime
import logging
import io
import os
import json
import copy
from collections import defaultdict

import numpy
from numpy.lib.recfunctions import append_fields
from PIL import Image as pImage
import pandas

from django.views import generic
from django.shortcuts import render, redirect
from django.db.models import Max, Min, Avg, Count, StdDev, Q
from django.http.response import HttpResponse, StreamingHttpResponse, HttpResponseRedirect
from django.urls.base import reverse_lazy
from django.http import JsonResponse

from django_filters.views import FilterView

from alob.dataio import export_images_excel, export_images_csv, export_images_result
from alob_plot.image import image_plot
from alob_plot.colors import *
from alob_plot.label_image import image_label_plot
from contrib.error import server_error
from .models import Image, Point, ImagePool
from .filter import ImageFilter
from .forms import ImageForm


log = logging.getLogger('alob')


DEFAULT_PAGINATION_BY = 100
DEFAULT_PAGINATE_ORPHANS = 10


APP_NAME = 'image'
APP_CLASS = Image


class IndexView(generic.ListView):
  
    template_name = '{}/index.html'.format(APP_NAME)
    paginate_orphans = DEFAULT_PAGINATE_ORPHANS
    paginate_by = DEFAULT_PAGINATION_BY

    def get_queryset(self):
        return APP_CLASS.objects\
                        .prefetch_related('points')\
                        .all()\
                        .order_by('date')
    def get_context_data(self, **kwargs):

        context = super(IndexView, self).get_context_data(**kwargs)
        points = Point.objects.all()
        context['points__count'] = points.count()
        # Eval point coords
        context.update(points.aggregate(Min('x'), Max('x'), Avg('x'), Min('y'), Max('y'), Avg('y')))
        context.update(Image.objects.annotate(Count('points')).aggregate(Avg('points__count'), Min('points__count'), Max('points__count'), StdDev('points__count')))
        # mean min distance per image
        min_distances_collection = []
        for image in Image.objects.all():
            pc = image.point_cloud()
            if pc.shape[0] > 0:
                m = pc[0] + 1j*pc[1]
                cm = numpy.hstack([(m,)*m.size])
                distances = numpy.abs(cm - cm.T)
                distances[numpy.where(distances==0.)] = 999.
                min_distances = numpy.min(distances, axis=0)
                min_distances_collection.extend(min_distances)
        if len(min_distances_collection):
            context['min_distances_avg'] = round(numpy.average(min_distances_collection),2)
            context['min_distances_min'] = round(numpy.min(min_distances_collection),2)
            context['min_distances_max'] = round(numpy.max(min_distances_collection),2)
            context['min_distances_stddev'] = round(numpy.std(min_distances_collection),2)
        return context

     
class IndexView_old(generic.ListView):
  
    template_name = 'image/index.html'
    context_object_name = 'images'

    def get_queryset(self):
        return Image.objects\
                    .prefetch_related('points')\
                    .all()

    def get_context_data(self, **kwargs):

        context = super(IndexView, self).get_context_data(**kwargs)
        points = Point.objects.all()
        context['points__count'] = points.count()
        # Eval point coords
        context.update(points.aggregate(Min('x'), Max('x'), Avg('x'), Min('y'), Max('y'), Avg('y')))
        context.update(Image.objects.annotate(Count('points')).aggregate(Avg('points__count'), Min('points__count'), Max('points__count'), StdDev('points__count')))
        # mean min distance per image
        min_distances_collection = []
        for image in Image.objects.all():
            pc = image.point_cloud()
            m = pc[0] + 1j*pc[1]
            cm = numpy.hstack([(m,)*m.size])
            distances = numpy.abs(cm - cm.T)
            distances[numpy.where(distances==0.)] = 999.
            min_distances = numpy.min(distances, axis=0)
            min_distances_collection.extend(min_distances)
        if len(min_distances_collection):
            context['min_distances_avg'] = round(numpy.average(min_distances_collection),2)
            context['min_distances_min'] = round(numpy.min(min_distances_collection),2)
            context['min_distances_max'] = round(numpy.max(min_distances_collection),2)
            context['min_distances_stddev'] = round(numpy.std(min_distances_collection),2)
        return context


class FilterView(FilterView):
    
    filterset_class = ImageFilter
    
    template_name = 'image/filter.html'

    def get(self, request, *args, **kwargs):
        filterset_class = self.get_filterset_class()
        self.filterset = self.get_filterset(filterset_class)
        self.object_list = self.filterset.qs
        context = self.get_context_data(filter=self.filterset,
                                        object_list=self.object_list)
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
        return self.render_to_response(context)

def export(request):
    columns = ['id', 'result', 'match',
               'first_id', 'second_id']
    df = pandas.DataFrame(list(Pair.objects\
                                   .filter(result__gt=0.1)\
                                   .order_by('-result')\
                                   .values(*columns)))
    # num points per image
    #d = dict(list(Image.objects.annotate(num_points=Count('points')).values_list('id', 'num_points')))
    d = {v['pk']: v for v in Image.objects.annotate(num_points=Count('points')).values('pk', 'num_points', 'date')}
    
    first_df = pandas.DataFrame([d[v] for v in df['first_id']])
    second_df = pandas.DataFrame([d[v] for v in df['second_id']])
    
    df['first_date'] = numpy.array(first_df['date'])
    df['first_num_points'] = numpy.array(first_df['num_points'])
    df['second_date'] = numpy.array(second_df['date'])
    df['second_num_points'] = numpy.array(second_df['num_points'])
    df['diff_num_points'] = numpy.abs(df['first_num_points'] - df['second_num_points'])

    
    # TODO, can bw done without temp file
    filename = tempfile.NamedTemporaryFile().name
    df.to_csv(filename, sep=';', encoding='utf-8', chunksize=5000, columns=columns+['first_date', 'first_num_points', 'second_date', 'second_num_points', 'diff_num_points'])
    # Excel writing takes forever
    #writer = pandas.ExcelWriter(filename, engine='xlsxwriter')
    #df.to_excel(writer, sheet_name='Alob Image', columns=columns+['first_date', 'first_num_points', 'second_date', 'second_num_points', 'diff_num_points'])
    #writer.save()

    response = HttpResponse(open(filename, 'rb').read())
    response['Content-Disposition'] = "attachment; filename=alob_images_%s.csv"%datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    return response


    
class DetailView(generic.DetailView):
  
    model = Image
    template_name = 'image/detail.html'

    def get_queryset(self):
        return Image.objects\
                    .prefetch_related('points')\
                    .all()

    def get_context_data(self, **kwargs):
        
        log.debug('get_context_data')
        
        context = super(DetailView, self).get_context_data(**kwargs)
        image = kwargs['object']

        if image.points.exists():
            points = image.pc_recarr()
            points = append_fields(points, 'color', [type2color(v) for v in points.type], usemask=False, asrecarray=True)
            context['plot_js'], context['plot_div'] = image_plot(points, plot_width=800, plot_height=600, create_components=True)
        else:
            context['plot_js'], context['plot_div'] = None, None
            log.warning('No Points Found')
        
        from pair.models import Pair        

        # Matches
        matches = []
        for p in Pair.objects.select_related('first', 'second').filter((Q(first_id=image.id) | Q(second_id=image.id)) & Q(match=True)):
            if p.first_id==image.id:
                match = p.second
            else:
                match = p.first
            matches.append([p, match])
        
        context['matches'] = matches
        
        #if Pair.objects.filter(first=image).exists():
        #    # scatter with all combinations
        #    fields = ['result', 'id']
        #    results = numpy.core.records.array(list(Pair.objects.filter(first=image).order_by('-result').values_list(*fields)), names=fields)
        #    context['result_plot_js'], context['result_plot_div'] = result_plot(results, plot_width=600, plot_height=600, create_components=True)
        
        return context


class LabelView(generic.DetailView):
  
    model = APP_CLASS
    template_name = '{}/label.html'.format(APP_NAME)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        if context is None:
            return server_error(message='No foto assigned to Image.\nLabeling not possible.')
        return generic.DetailView.get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        c = generic.DetailView.get_context_data(self, **kwargs)
        # set variables that no exceptions is raised with TEMPLATE_DEBUG on
        c['next'] = False
        c['previous'] = False
        
        obj = c['object']
        
        fields = ['id', 'x', 'y', 'type']
        if obj.points.exclude(type='wart').exists():
            img, x_min, y_min = obj.img(crop=True)
            points = pandas.DataFrame(list(obj.points.all().values(*fields))).set_index('id')
        else:
            img, x_min, y_min = obj.img(crop=False)
            if img is None:
                return None
            x,y = img.size
            data = [{'id': None, 'x': 100, 'y': y/2, 'type': 'nose'},
                    {'id': None, 'x': x-100, 'y': y/2, 'type': 'tail'},
                    {'id': None, 'x': 200, 'y': y/2-100, 'type': 'left_eye'},
                    {'id': None, 'x': 200, 'y': y/2+100, 'type': 'right_eye'},
                    ]
            data += list(obj.points.all().values(*fields))
            points = pandas.DataFrame(data=data, columns=fields).set_index('id')
            

        points['color'] = points.type.apply(type2color)

        #points.x -= x_min
        #points.y -= y_min
        data_url = reverse_lazy('image:json_update_point', kwargs=dict(pk=obj.pk))   
        main_url = reverse_lazy('image:detail', kwargs=dict(pk=obj.pk))   
        c['plot_js'], c['plot_div'] = image_label_plot(img, points, data_url, main_url, offset=(x_min, y_min))

        #
        # check if we are in labeling mode of a pool
        #
        if 'pool' in self.request.GET.keys():
            pool = ImagePool.objects.filter(pk=self.request.GET['pool'])
            if pool.exists():
                pool = pool.first()
                pids = list(pool.images.filter(is_labeled=False).values_list('pk', flat=True))
                if pids.count(obj.id):
                    index = pids.index(obj.id)
                else:
                    index = 0
                if pids:
                    c['next'] = str(reverse_lazy('image:label', kwargs=dict(pk=pids[(index + 1)%len(pids) ]))) + '?pool={}'.format(pool.pk)
                    c['previous'] = str(reverse_lazy('image:label', kwargs=dict(pk=pids[index - 1]))) + '?pool={}'.format(pool.pk)
        return c


class RotateView(generic.DetailView):
    
    model = APP_CLASS
    
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        pImage.open(obj.image.path).rotate(180).save(obj.image.path)
        return HttpResponseRedirect(reverse_lazy('{}:detail'.format(APP_NAME), kwargs=dict(pk=obj.pk)))


class DeletePointView(generic.DeleteView):
    
    model = Point
    
    def get_success_url(self):
        im = self.object.image
        return reverse_lazy('{}:detail'.format(APP_NAME), kwargs=dict(pk=im.pk))

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class DeletePointsView(DetailView):
    
    model = APP_CLASS
    
    def get_context_data(self, **kwargs):
        obj = self.get_object()
        obj.points.all().delete()
        return {}
    
    def get(self, request, *args, **kwargs):
        DetailView.get(self, request, *args, **kwargs)
        return redirect(reverse_lazy('image:detail', kwargs=dict(pk=self.object.pk)))

class JSONUpdatePointView(generic.DetailView):
    
    model = APP_CLASS
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        data = json.loads(request.body.decode("utf-8"))

        pids = list(self.object.points.all().values_list('pk', flat=True))
        log.debug('IDs of points defined on image: {}'.format(pids))

        for id,x,y,ptype in zip(data['id'], data['x'], data['y'], data['type']):
            # Edit
            if id and id != 'NaN':
                if id > 0:
                    print('Update Point: {} -> ({},{})'.format(id,x,y))
                    Point.objects.filter(pk=id).update(x=x, y=y)
                    log.debug('Remove from list to delete: {}'.format(id))
                    pids.remove(id)
            # Add Point            
            else:
                Point.objects.create(image=self.object, x=x, y=y, type=ptype)
        
        # delete points not in list
        log.debug('Delete Points: {}'.format(pids))
        Point.objects.filter(pk__in=pids).delete()
        
        if not self.object.is_labeled:
            self.object.is_labeled = True
            self.object.save()
        return JsonResponse(data=dict(message='Points Updated.'))


class ResultView(generic.ListView):
  
    model = Image
    template_name = 'image/result.html'

    def get_queryset(self):
        return Image.objects\
                    .prefetch_related('points')\
                    .all()

    def get(self, request, *args, **kwargs):
        
        if 'csv' in request.GET.keys():
            d = self.get_context_data()['object_list']
            output = export_images_result(pandas.DataFrame(d))
            response = StreamingHttpResponse(output,
                                             content_type="text/csv")
            response['Content-Disposition'] = 'attachment; filename="ImagesResults.csv"'
            return response            

        return generic.ListView.get(self, request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):

        from pair.models import Pair

        firsts = Image.objects.filter(first__match=1).values_list('id', flat=True)
        seconds = Image.objects.filter(second__match=1).values_list('id', flat=True)
        ids = set(list(firsts)+list(seconds))
        dfi  = pandas.DataFrame(list(Image.objects.filter(id__in=ids).order_by('date').distinct().values('id', 'name', 'date')))
        dfp = pandas.DataFrame(list(Pair.objects.filter(match=1).values('first_id', 'second_id')))
        
        dsecond = dfi.join(dfp.set_index('second_id'), on='id', how='left').dropna()
        dfirst = dfi.join(dfp.set_index('first_id'), on='id', how='left').dropna()
        dsecond.rename(columns={'first_id': 'second_id'}, inplace=True)
        
        dr = pandas.concat([dfirst, dsecond])
        dr = dr.join(dfi.set_index('id'), on='second_id', rsuffix='_second')
        dr['second_id'] = dr['second_id'].astype(int)
        dr['time_diff'] = (dr['date_second'] - dr['date']).map(lambda x: x.days)
        
        return dict(object_list=dr.to_dict('records'))


class ResultCmrView(generic.TemplateView):
  
    model = Image
    template_name = 'image/result_cmr.html'

    def get_queryset(self):
        return Image.objects\
                    .prefetch_related('points')\
                    .all()

    def get(self, request, *args, **kwargs):
        
        if 'export' in request.GET.keys():
            d = self.get_context_data()['data']
            out_s = ''
            for v in d:
                out_s += '\t'.join([str(w) for w in v]) + '\n'
            response = StreamingHttpResponse(out_s,
                                             content_type="text/plain")
            response['Content-Disposition'] = 'attachment; filename="Alob_Capture-Mark-Recapture.txt"'
            return response            

        return generic.TemplateView.get(self, request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):

        from pair.models import Pair

        matches = pandas.DataFrame(list(Pair.objects.filter(match=1)\
                                            .values_list('first_id', 'second_id')), 
                                   columns=['first_id', 'second_id'])
        matches.set_index('first_id', inplace=True)
        
        images_with_matches = []
        d = defaultdict(set)
        for i,v in matches.iterrows():
            d[i].add(i)
            d[i].add(v['second_id'])
            images_with_matches.extend([i, v['second_id']])
            
        images_with_matches = list(set(images_with_matches))
        
        # create copy, iterate and delete entries is not a good idea
        nd = copy.deepcopy(d)
        for k,v in d.items():
            for w in list(v)[1:]:
                w in nd and nd.pop(w)
        
        # Extend with all other images
        for i in Image.objects.exclude(id__in=images_with_matches).order_by('date').values_list('id', flat=True):
            nd[i].add(i)
        
        dates = numpy.unique(Image.objects.filter(date__isnull=False).values_list('date', flat=True))
        dates.sort()
        locations = numpy.unique(Image.objects.filter(location__isnull=False).values_list('location', flat=True))
        locations.sort()
        
        locations_legend = [(v[0], v) for v in locations]
        
        dates_dict = dict([(v,k) for k,v in enumerate(dates)])
        indi_dict = dict([(v,k) for k,v in enumerate(nd.keys())])
        
        arr = numpy.zeros(shape=(len(nd), len(dates_dict)), dtype=numpy.int64).astype(str)
        
        indi_ids = []
        for k,v in nd.items():
            for w in v:
                im = Image.objects.get(pk=w)
                arr[indi_dict[k],dates_dict[im.date]] = im.location and im.location[0] or '0'
            indi_ids.append(w)
        
        header = [['ID'] + [v.strftime('%Y-%m-%d') for v in dates]]
        result = header + [[indi_ids[i]]+v.tolist() for i,v in enumerate(arr)]

        num_images = Image.objects.count()
        
        return dict(data=result, num_images=num_images, locations_legend=locations_legend)


def marked_image_jpeg(request, pk, width=300, crop=True):
    i = Image.objects.get(pk=pk)
    mark = True
    width=int(width)
    if 'small' in request.GET.keys():
        mark = False
    img = i.marked_image(crop=crop, mark=mark)
    response = HttpResponse(content_type="image/jpeg")
    response['Content-Disposition'] = 'attachment; filename="%s_marked.jpg"'%i.name
    buf = io.BytesIO()
    #im = pImage.fromarray(img)
    # TODO fix me
    if 'small' in request.GET.keys():
        f = width/img.size[0]
        img = img.resize( [width, int(f*img.size[1])], pImage.ANTIALIAS )
    img.convert('RGB').save(buf, format='jpeg')
    img = buf.getvalue()
    buf.close()
    response.write(img)
    return response


def image_jpeg(request, pk):
    i = Image.objects.get(pk=pk)
    img, _, _ = i.img()
    response = HttpResponse(content_type="image/jpeg")
    response['Content-Disposition'] = 'attachment; filename="%s.jpg"'%i.name
    if 'small' in request.GET.keys():
        width=300
        f = width/img.shape[1]
        im = im.resize( [width, int(f*img.shape[0])], pImage.ANTIALIAS )
    #im = im.resize( [int(0.8*s) for s in im.size], pImage.ANTIALIAS )
    buf = io.BytesIO()
    img.convert('RGB').save(buf, format='jpeg')
    img = buf.getvalue()
    buf.close()
    response.write(img)
    return response


def import_excel(request):
    
    template_name = '{}/import.html'.format(APP_NAME)
    
    image_pools = ImagePool.objects.all()
    
    if request.method == 'POST':

        image_file = request.FILES.get('image_file', None)
        images = request.FILES.getlist('images')
        images = dict([(os.path.basename(image.name), image) for image in images])
        new_pool = request.POST.get('new_pool', False)
        pool = request.POST.get('pool', False)
        pools = request.POST.getlist('pools')

        errors = []

        if new_pool and not pool:
            errors.append('Please provide a Name for the Pool to be created.')
            return render(request=request,
                          template_name=template_name,
                          context={'errors': errors, 'pools': image_pools})
        
        #
        # Create the pool if set
        #
        if new_pool:
            pool = ImagePool.objects.create(name=pool)
            pools.append(pool)
        
        
        # only images provided
        if image_file is None:
            idf = None
        # image file to be read
        else:
        
            # Validate the files
            if image_file.name.endswith('.csv'):
                idf = pandas.read_csv(image_file, delimiter=';')
            elif image_file.name.endswith('.xlsx'):
                idf = pandas.read_excel(image_file)
            else:
                errors.append('Wrong file format for Image file. Supported files are xlsx and csv.')
    
            if errors:
                return render(request=request,
                              template_name=template_name,
                              context={'errors': errors, 'pools': image_pools})
            
            idf = idf.fillna('')
            idf.set_index('image', inplace=True)

        #
        # Create the images        
        #
        num_created = 0
        for image_name, image in images.items():
            data = dict(image=image)
            #db_im = Image.objects.create(image=image)
            if idf is None:
                data['name'] = image_name
            else:
                if image_name in idf.name.keys():
                    image_data = idf.loc[image_name].to_dict()
                    print(data)
                    data.update(image_data)
                else:
                    errors.append('Image {} not in Image Data.'.format(image_name))
            
            try:
                dim = Image.objects.create(**data)
                dim.pools.set(pools)
                num_created += 1
            except Exception as e:
                data.pop('image')
                errors.append('Cannot create image with {}\n{}'.format(json.dumps(data), str(e)))
                continue            

        #
        # Assign to pools
        #
        
        
        
        return render(request=request, 
                      template_name=template_name,
                      context=dict(finished=True,
                                   num_created=num_created,
                                   pools=image_pools,
                                   errors=errors, log=None))
    else:
        c = dict(pools=ImagePool.objects.all())
        return render(request=request,
                      template_name=template_name,
                      context=c)


class CreateView2(generic.CreateView):

    model = APP_CLASS
    success_url = reverse_lazy('%s:index' % APP_NAME)
    template_name = '{}/form.html'.format(APP_NAME)
    fields = ('name', 'image', 'project', 'name', 'date', 'location', 'juvenile', 'has_eggs', 'operator', 'quality', 'disabled', 'comment')

    def get_initial(self):
        project = ([''] + sorted(set(Image.objects.filter(project__isnull=False).values_list('project', flat=True))) ).pop()
        date = datetime.datetime.today()
        return {'project': project,
                'date': date}


class CreateView(generic.CreateView):

    model = APP_CLASS
    template_name = '{}/form.html'.format(APP_NAME)
    form_class = ImageForm

    def get_initial(self):
        project = ([''] + sorted(set(Image.objects.filter(project__isnull=False).values_list('project', flat=True))) ).pop()
        date = datetime.datetime.today()
        return {'project': project,
                'date': date}
    
    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        self.object = form.save()
        pools = form.cleaned_data.get('pools', False)
        if pools:
            self.object.pools.set(pools)
        return super(CreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('image:detail', kwargs={'pk': self.object.pk})


class UpdateView(generic.UpdateView):
 
    model = APP_CLASS
    success_url = reverse_lazy('%s:index' % APP_NAME)
    template_name = '{}/form.html'.format(APP_NAME)
    fields = ('project', 'name', 'image', 'date', 'location', 'juvenile', 'has_eggs', 'operator', 'quality', 'disabled', 'comment')
 
    def get_success_url(self):
        return self.request.GET.get('next', self.success_url)


class DeleteView(generic.DeleteView):
    
    model = APP_CLASS
    success_url = reverse_lazy('%s:index' % APP_NAME)

    def get_success_url(self):
        return self.request.GET.get('next', self.success_url)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)