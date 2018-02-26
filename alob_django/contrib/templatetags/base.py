'''
Alob Project
2016
Author(s): R.Walker

'''
from math import floor

from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from docutils.core import publish_parts

register = template.Library()

@register.filter
def rst(v):
    p = publish_parts(source=v, writer_name='html5_polyglot')['html_body']
    return mark_safe(p.replace('src="./', 'src="/static/images/doc/'))

@register.filter
def red(v):
    if v is None:
        v = 0.
    cv = int(120+v*(256-120))
    return '#ff%02x%02x' % (cv, cv)

@register.filter
def glyphicon(name, uid='', color=''):
    if uid != '':
        uid = ' id=%s'%uid
    if color != '':
        color = ' style="color: {}"'.format(color)
    return format_html('<i class="glyphicon glyphicon-{}"{}{}></i>', name, uid, mark_safe(color))

@register.filter
def fa(name, uid=''):
    if uid != '':
        uid = ' id=%s'%uid
    return format_html('<i class="fa fa-arrows-h" aria-hidden="true"></i>', name, uid)

@register.simple_tag
def play():
    return glyphicon('play')

@register.simple_tag
def stop():
    return glyphicon('stop')

@register.simple_tag
def pair():
    return fa('arrows-h')

@register.simple_tag
def pool():
    return glyphicon('th')

@register.simple_tag
def search():
    return glyphicon('search')

@register.simple_tag
def add():
    return glyphicon('plus')

@register.simple_tag
def new():
    return glyphicon('plus')

@register.simple_tag
def tlist():
    return glyphicon('th-list')

@register.simple_tag
def delete():
    return glyphicon('trash')

@register.simple_tag
def edit():
    return glyphicon('edit')

@register.simple_tag
def download():
    return glyphicon('download')

@register.simple_tag
def import_tag():
    return glyphicon('import')

@register.simple_tag
def plot():
    return glyphicon('signal')

@register.simple_tag
def down(uid=''):
    return glyphicon('chevron-down', uid=uid)

@register.simple_tag
def up(uid=''):
    return glyphicon('chevron-up', uid=uid)

@register.simple_tag
def save():
    return glyphicon('save')

@register.simple_tag
def show(color=None):
    return glyphicon('eye-open', color=color)

@register.simple_tag
def refresh(color=None):
    return glyphicon('refresh', color=color)

@register.simple_tag
def label(color=None):
    return glyphicon('pencil', color=color)

@register.simple_tag
def next(color=None):
    return glyphicon('step-forward', color=color)

@register.simple_tag
def previous(color=None):
    return glyphicon('step-backward', color=color)

@register.filter
def timedelta(value, time_format="{days} days, {hours2}:{minutes2}:{seconds2}"):

    if hasattr(value, 'seconds'):
        seconds = value.seconds + value.days * 24 * 3600
    else:
        seconds = int(value)

    seconds_total = seconds

    minutes = int(floor(seconds / 60))
    minutes_total = minutes
    seconds -= minutes * 60

    hours = int(floor(minutes / 60))
    hours_total = hours
    minutes -= hours * 60

    days = int(floor(hours / 24))
    days_total = days
    hours -= days * 24

    years = int(floor(days / 365))
    years_total = years
    days -= years * 365

    return time_format.format(**{
        'seconds': seconds,
        'seconds2': str(seconds).zfill(2),
        'minutes': minutes,
        'minutes2': str(minutes).zfill(2),
        'hours': hours,
        'hours2': str(hours).zfill(2),
        'days': days,
        'years': years,
        'seconds_total': seconds_total,
        'minutes_total': minutes_total,
        'hours_total': hours_total,
        'days_total': days_total,
        'years_total': years_total,
    })
