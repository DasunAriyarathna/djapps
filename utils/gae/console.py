import code, getpass, sys, os

def setup_gae_console(app_id, host = "localhost:8080", gae_path = "/opt/google/google_appengine"):
    if gae_path not in sys.path:
        sys.path.append(gae_path)
        sys.path.append(gae_path + "/lib/yaml/lib")
        sys.path.append(gae_path + "/lib/fancy_urllib")
        # sys.path.append(os.path.abspath("."))
        # sys.path.append(os.path.abspath("../django.zip"))

    os.environ['DJANGO_SETTINGS_MODULE']    = "settings"
    os.environ['APPLICATION_ID']            = app_id

    import urllib2
    from djapps.utils import proxy
    opener = urllib2.build_opener(proxy.SkippableProxyHandler(["localhost", "localhost:8080"]))
    urllib2.install_opener(opener)

    return register_stubs(app_id, host)

def register_stubs(app_id, host):
    print sys.path
    import google
    import google.appengine
    from google.appengine.ext import remote_api
    from google.appengine.ext.remote_api import remote_api_stub
    from google.appengine.api import apiproxy_stub_map
    from google.appengine.api import datastore_file_stub
    from google.appengine.api.memcache import memcache_stub
    from google.appengine.api import mail_stub

    apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
    apiproxy_stub_map.apiproxy.RegisterStub('memcache', memcache_stub.MemcacheServiceStub()) 
    apiproxy_stub_map.apiproxy.RegisterStub('mail', mail_stub.MailServiceStub()) 
    apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', datastore_file_stub.DatastoreFileStub(app_id, '/dev/null', '/dev/null'))

    # disable proxy for local hosts
    if  host.lower().find("localhost") >= 0:
        print "Deploying to development server: ", host, "...."
        os.environ['http_proxy']    = ""
        os.environ['HTTP_PROXY']    = ""
        os.environ['https_proxy']   = ""
        os.environ['HTTPS_PROXY']   = ""
        secure                      = False
        production                  = False
    else:
        print "Deploying to production server: ", host, "...."
        secure                      = True 
        production                  = True

    def auth_func():
        print "Authenticating....."
        username = os.environ.get("GAE_USERNAME", None)
        password = os.environ.get("GAE_PASSWORD", None)
        if username is None:
            username = getpass.getpass('Could not find GAE_USERNAME environment variable.  \n' +
                                        'Please enter Username: ')
        if password is None:
            password = getpass.getpass('Could not find GAE_PASSWORD environment variable.  \n' +
                                        'Please enter Password: ')
        return username, password

    remote_api_stub.ConfigureRemoteDatastore(app_id, '/remote_api', auth_func, host, secure = secure)
    return production

