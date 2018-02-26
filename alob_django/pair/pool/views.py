from django.views import generic

from django.urls.base import reverse_lazy
from django.http.response import HttpResponseRedirect

from pair.models import Pair, PairPool

APP_CLASS = PairPool
APP_NAME = 'pair:pool'
APP_PATH = 'pair/pool'


class ListView(generic.ListView):

    template_name_suffix = ''
    model = APP_CLASS
    template_name = "%s/index.html" % APP_PATH


class DetailView(generic.DetailView):

    model = APP_CLASS
    template_name = "%s/detail.html" % APP_PATH


class CreateView(generic.CreateView):

    model = APP_CLASS
    template_name = "%s/form.html" % APP_PATH
    success_url = reverse_lazy('%s:index' % APP_NAME)
    fields = ('name',)

    def get_success_url(self):
        return self.request.GET.get('next', self.success_url)

    def form_valid(self, form):
        if not self.request.user.is_staff:
            form.instance.owner = self.request.user
        return super(CreateView, self).form_valid(form)


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
        c['object'] = PairPool.objects.get(pk=self.kwargs['pk'])
        return c
