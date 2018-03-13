'''
Alob Project
2016 -2018
Author(s): R.Walker

'''
import io
import pandas


def export_images_excel(object_list):
    output = io.BytesIO()
    writer = pandas.ExcelWriter(output, engine='xlsxwriter', options={'encoding': 'utf-8', 'remove_timezone': True})
    df = pandas.DataFrame(list(object_list.values()))
    df.to_excel(writer, sheet_name='Images', index=False, startrow=0, startcol=0, encoding='utf-8')
    writer.save()
    return output.getvalue()