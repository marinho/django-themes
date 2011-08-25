## How it works

Basically:

- the applications register their templates they are able to load from Themes (this is important
  for security, but there's a setting to allow not registered templates with standard configuration);
- each Theme has the templates the project registered;
- a Theme is set as default Theme, but a function can set it dinamically from the current request;
- when a template is required, our template loader tries to load it from current Theme, if it finds,
  so returns that template (instead from file system);
- you can upload static files for the themes;
- you can download and import themes;
- works with Django's template renderer and Jinja2 (still in development).

## Testing

If you want to test, do this (somewhere):

    $ git clone git://github.com/marinho/django-themes.git
    $ cd django-themes
    $ virtualenv env
    $ source env/bin/activate
    $ pip install -r test_project/requirements.txt
    $ cd test_project
    $ ln -s ../themes .
    $ python manage.py syncdb
    $ python manage.py runserver

So you are able to visit in the browser:

- http://localhost:8000/ - firstly this will show a "Template not found" error
- http://localhost:8000/themes/ - here you can create your first template and write something
- http://localhost:8000/ - come back here to see it working

