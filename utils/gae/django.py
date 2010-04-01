import logging, os, sys

def setup_django(django_dir = "Django-1.1", django_zip = "django1.1.zip", server_software = None):
    # remove the standard version of django - django 0.96
    for k in [ k for k in sys.modules if k.lower().startswith('django') ]:
        logging.debug(" ========== Deleting Module: " + k + ", " + str(sys.modules[k]))
        del sys.modules[k]

    # force sys.path to have our own directory first in 
    # case we want to import from it
    django_path = django_zip
    logging.debug("Using Prod Server ===============")

    if not server_software:
        server_software = os.environ.get('SERVER_SOFTWARE',"")

    print >> sys.stderr, "=" * 80
    print >> sys.stderr, "Server Software: ", server_software

    # Set logging and use the real django folders instead of
    # django zip in dev mode
    if server_software.startswith('Dev'):
        logging.debug("Using Dev Server ===============" + os.path.abspath(os.curdir))
        django_path = django_dir
        logging.getLogger().setLevel(logging.DEBUG)

    sys.path.insert(0, django_path)

    # Must set this env var before importing any part of Django
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
