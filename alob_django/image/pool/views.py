'''
Alob Project
2016 - 2018
Author(s): R.Walker

'''
from itertools import combinations

from django.views import generic

from django.urls.base import reverse_lazy
from django.http.response import HttpResponseRedirect
from django.db.models import Q

from image.models import Image, ImagePool
from pair.models import Pair, PairPool

from .forms import ImagePoolForm

APP_CLASS = ImagePool
APP_NAME = 'image:pool'
APP_PATH = 'image/pool'


class ListView(generic.ListView):

    template_name_suffix = ''
    model = APP_CLASS
    template_name = "%s/index.html" % APP_PATH


class DetailView(generic.DetailView):

    model = APP_CLASS
    template_name = "%s/detail.html" % APP_PATH

    def get_context_data(self, **kwargs):
        context = generic.DetailView.get_context_data(self, **kwargs)
        obj = context['object']
        
        matches = Pair.objects.order_by().filter(match=1) 
        pool_matches = matches.filter(first__pools=obj, second__pools=obj)
        context['pool_matches'] = pool_matches
        context['first_matches'] = Pair.objects.filter(match=1).filter(Q(first__pools=obj) & ~Q(second__pools=obj))
        context['second_matches'] = Pair.objects.filter(match=1).filter(Q(second__pools=obj) & ~Q(first__pools=obj))
        context['num_matches_other_pools'] = context['first_matches'].count() + context['second_matches'].count()
        return context

class ImagesView(generic.ListView):

    model = Image
    template_name = "%s/images.html" % APP_PATH
    paginate_orphans = 20
    paginate_by = 50

    def get_queryset(self):
        return Image.objects.filter(pools=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        c = generic.ListView.get_context_data(self, **kwargs)
        c['object'] = ImagePool.objects.get(pk=self.kwargs['pk'])
        return c

# TODO
# use this approach: https://docs.djangoproject.com/en/1.11/topics/class-based-views/mixins/#using-singleobjectmixin-with-listview

class PairsView(generic.ListView):

    model = Pair
    template_name = "%s/pairs.html" % APP_NAME
    paginate_orphans = 10
    paginate_by = 30

    def get_queryset(self):
        return Pair.objects\
                   .filter(first__pools=self.kwargs['pk'])\
                   .prefetch_related('first', 'second', 'first__points', 'second__points')\
                   .all()\
                   .order_by('-result')
    
    def get_context_data(self, **kwargs):
        c = generic.ListView.get_context_data(self, **kwargs)
        c['object'] = ImagePool.objects.get(pk=self.kwargs['pk'])
        return c



class CreateView(generic.CreateView):

    model = APP_CLASS
    template_name = "%s/form.html" % APP_PATH
    success_url = reverse_lazy('%s:index' % APP_NAME)
    form_class = ImagePoolForm

    def get_success_url(self):
        return self.request.GET.get('next', self.success_url)


class UpdateView(generic.UpdateView):

    model = APP_CLASS
    template_name = "%s/form.html" % APP_PATH
    success_url = reverse_lazy('%s:index' % APP_NAME)
    fields = ('name',)

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


class LabelView(generic.DetailView):

    model = APP_CLASS
    
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        # are there unlabeled data?
        labeled = obj.images.filter(is_labeled=False)
        if labeled.exists():
            image = labeled.first()
        else:
            image = obj.images.first()
        if image:
            url = reverse_lazy('image:label', kwargs={'pk': image.pk})
            url = str(url) + '?pool={}'.format(obj.pk)
            return HttpResponseRedirect(redirect_to=url)
        else:
            return HttpResponseRedirect(redirect_to=reverse_lazy('image:pool:detail', kwargs={'pk': obj.pk}))
    
    

class GeneratePairPoolView(generic.RedirectView, generic.DetailView):
    
    model = APP_CLASS

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        pk = self.object.pk
        
        # Select images
        image_ids = Image\
                    .objects\
                    .filter(pools=pk,\
                            is_labeled=True)\
                    .values_list('pk', flat=True)
    
        # Pair generation
        pairs = list(combinations( image_ids,  2))
        num_pairs = len(pairs)
        pair_pks = []
        for f,s in pairs:
            pair = Pair.objects.filter(first_id__in=[f,s], second_id__in=[f,s]).first()
            if pair is None:
                pair = Pair.objects.create(first_id=f, second_id=s)
            pair_pks.append(pair.pk)
        # Generate Pair Pool
        pp = PairPool.objects.create(name=self.object.name + '-pairs')
        pp.pairs.set(pair_pks)
        url = reverse_lazy('pair:pool:detail'.format(), kwargs=dict(pk=pp.pk))
        return HttpResponseRedirect(url)
