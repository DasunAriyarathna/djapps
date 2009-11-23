import code, getpass, sys, os

sys.path.append("/opt/google/google_appengine")
sys.path.append("/opt/google/google_appengine/lib/yaml/lib")
# sys.path.append(os.path.abspath("."))
# sys.path.append(os.path.abspath("../django.zip"))

from google.appengine.ext import db

if len(sys.argv) < 2:
    print "Usage: %s app_id [host]" % sys.argv[0]
    sys.exit(1)

app_id              = sys.argv[1]
host                = "%s.appspot.com" % app_id
batch_save_limit    = 250

if len(sys.argv) > 2:
    host = sys.argv[2]

os.environ['DJANGO_SETTINGS_MODULE']    = "settings"
os.environ['APPLICATION_ID']            = app_id

def auth_func():
    print "Authenticating....."
    if 'GAE_PASSWORD' in os.environ:
        return 'sri.panyam@gmail.com', os.environ['GAE_PASSWORD']
    else:
        return 'sri.panyam@gmail.com', getpass.getpass('Password:')

def register_stubs(app_id, host):
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
        batch_save_limit            = 1000
        os.environ['http_proxy']    = ""
        os.environ['HTTP_PROXY']    = ""
        os.environ['https_proxy']   = ""
        os.environ['HTTPS_PROXY']   = ""
        secure                      = False
    else:
        print "Deploying to production server: ", host, "...."
        secure                      = True 

    remote_api_stub.ConfigureRemoteDatastore(app_id, '/remote_api', auth_func, host, secure = secure)

register_stubs(app_id, host)
