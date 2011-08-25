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

