import math

import numpy
from scipy import stats

from bokeh.plotting import figure, ColumnDataSource
from bokeh.io import output_file, save#, show
from sklearn.preprocessing.data import MinMaxScaler#StandardScaler, RobustScaler
from bokeh.models.tools import HoverTool, TapTool
from bokeh.models.callbacks import OpenURL

#
# TODO
# split the data in matches and no-matches and visualize them separatley (left, right side of the violin)
#


features = numpy.load('features.npy')
pairs = numpy.load('pairs.npy')

columns = features.dtype.names

hover = HoverTool(tooltips=[("id", "@id"), ('result', '@result')])

plot = figure(x_range=columns, 
              width=1600, height=800,
              tools=['pan', 'wheel_zoom', 'tap', hover])
plot.xaxis.major_label_orientation = math.pi/3
url = "http://127.0.0.1:8000/pair/@id/"
taptool = plot.select(type=TapTool)
taptool.callback = OpenURL(url=url)

scaler = MinMaxScaler()
features = scaler.fit_transform(X=features.view((numpy.float64, len(features.dtype.names))))


offset = 1

for i,column in list(enumerate(columns))[:]:

    print('Column: {}'.format(column))
    ix = i*offset+0.5
    # data prepare
    data = features.T[i]
    # scale
    kde = stats.gaussian_kde(data)
    grid = numpy.linspace(data.min(), data.max(), 80)
    result = kde(grid)
    result /= 2*result.max()
    
    x_patch = numpy.append(result, -result[::-1])
    y_patch = numpy.append(grid, grid[::-1])
    # violin
    plot.patch(x_patch+ix, y_patch, alpha=1, color='lightgrey', line_color='grey', line_width=1)
    
    # Matches
    idx = numpy.where(pairs.match==1)
    y = data[idx]
    x = numpy.zeros(y.shape)+ix
    index = pairs[idx].id
    src = ColumnDataSource(data=dict(x=x, y=y, id=index, fill_color=['red']*len(id)))
    plot.circle(source=src, size=6, x='x', y='y', id='id', line_color='fill_color', fill_color='fill_color')
    # Prediction
    #y = data
    #x = numpy.zeros(y.shape)+ix+0.2
    #plot.scatter(x, y, color='yellow', marker='cross')


output_file('feature_violin.html')
save(plot)