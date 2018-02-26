Create Test Subset
------------------


Open *python manage.py shell_plus*

::


    import shutil
    image_ids =  [1, 362, 652, 789, 673, 854, 365, 503, 73, 750, 326, 12]
    mkdir media_min
    for img in Image.objects.filter(id__in=image_ids):
        shutil.copy2(img.image.path, 'media_min/{}'.format(img.image.name))

    from django.core import serializers
    objs = list(Image.objects.filter(id__in=image_ids)) + list(Point.objects.filter(image_id__in=image_ids)) + list(Pair.objects.filter(first_id__in=image_ids, second_id__in=image_ids))
    img_json = serializers.serialize('json', objs)
    open('data.json', 'w').write(img_json)
    
    
    python manage.py dumpdata image pair prediction > dump.json
    
    python manage.py loaddata dump.json
    