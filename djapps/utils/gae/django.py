
def setup_django(django_dir = "Django-1.1.2", django_zip = "django1.1.2.zip", server_software = None):
    """
    Sets up django for use with app engine.
    """

    import logging, os, sys
    # remove the standard version of django - django 0.96
    for k in [ k for k in sys.modules if k.lower().startswith('django') ]:
        logging.debug(" ========== Deleting Module: " + k + ", " + str(sys.modules[k]))
        del sys.modules[k]

    if not server_software:
        server_software = os.environ.get('SERVER_SOFTWARE',"")

    # Set logging and use the real django folders instead of
    # django zip in dev mode
    if server_software.startswith('Dev'):
        django_path = django_dir
    else:
        django_path = django_zip

    logging.getLogger().setLevel(logging.DEBUG)

    if django_path not in sys.path:
        sys.path.insert(0, django_path)

    print >> sys.stderr, "Path: ", django_dir, django_path, sys.path

    # Must set this env var before importing any part of Django
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
