import zipfile
import os
import random
import shutil
import glob

from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.core.files.base import ContentFile

from models import Theme

def dump_file_name(sf):
    try:
        return os.path.split(sf.file.name)[-1]
    except ValueError:
        return None

def export_theme(theme):
    """
    Outputs a zipfile with the theme, its templates and static files.
    """
    dir_name = ''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for n in range(20)])
    work_dir = os.path.join('/tmp/', dir_name)
    os.makedirs(work_dir)
    os.chdir(work_dir)

    zipf_path = os.path.join(work_dir, 'theme-%s.zip'%theme.name)
    zipf = zipfile.ZipFile(zipf_path, 'w')

    json = {
        'name': theme.name,
        'verbose_name': theme.verbose_name,
        'templates': [{
            'name': tpl.name,
            'notes': tpl.notes,
            'content': tpl.content,
            'engine': tpl.engine,
            } for tpl in theme.templates.all()],
        'static_files': [{
            'name': sf.name,
            'url': sf.url,
            'file': dump_file_name(sf),
            'mime_type': sf.mime_type,
            } for sf in theme.static_files.all()],
        }
    jsonf_path = 'details.json'
    json_fp = file(jsonf_path, 'w')
    json_fp.write(simplejson.dumps(json))
    json_fp.close()

    zipf.write(jsonf_path)

    for sf in theme.static_files.exclude(file__isnull=True).exclude(file=''):
        try:
            f_name = dump_file_name(sf)
            shutil.copyfile(sf.file.path, os.path.join(work_dir, f_name))
            zipf.write(f_name)
        except ValueError:
            pass

    zipf.close()

    return zipf_path

def import_theme(zipfp):
    # Initializes the working area
    dir_name = ''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for n in range(20)])
    work_dir = os.path.join('/tmp/', dir_name)
    os.makedirs(work_dir)
    os.chdir(work_dir)

    # Opens and extracts the zip file
    zipf = zipfile.ZipFile(zipfp)
    zipf.extractall()

    # Loads driver JSON file
    json_fp = file('details.json')
    json = simplejson.loads(json_fp.read())
    json_fp.close()

    # Doesn't allow import existing theme (must delete before)
    if Theme.objects.filter(name=json['name']).count():
        raise ValueError(_('Theme "%s" already exists.')%json['name'])

    # Creates the new theme
    theme = Theme.objects.create(name=json['name'], verbose_name=json['verbose_name'])

    # Creates the new templates
    for json_tpl in json['templates']:
        tpl, new = theme.templates.get_or_create(name=json_tpl['name'])
        tpl.content = json_tpl['content']
        tpl.notes = json_tpl['notes']
        tpl.engine = json_tpl['engine']
        tpl.save()

    # Creates the new static files
    for json_sf in json['static_files']:
        sf = theme.static_files.create(
                name=json_sf['name'],
                url=json_sf['url'],
                mime_type=json_sf['mime_type'],
                )

        if json_sf['file']:
            fp = file(json_sf['file'])
            content = ContentFile(fp.read())
            fp.close()

            file_name = json_sf['file']
            while os.path.exists(file_name):
                file_name += '_'

            sf.file.save(file_name, content)
            sf.save()

    return theme

