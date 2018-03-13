'''
Alob Project
2016 -2018
Author(s): R.Walker

'''
import io
import pandas

def export_images_csv(object_list):
    output = io.StringIO()
    df = pandas.DataFrame(list(object_list.values()))
    df.to_csv(output, index=False, encoding='utf-8')
    return output.getvalue()

def export_images_result(df):
    output = io.StringIO()
    df.to_csv(output, index=False, encoding='utf-8')
    return output.getvalue()
    