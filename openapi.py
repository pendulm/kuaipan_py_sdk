# coding: utf-8
import json
import urllib

from utils import generate_signature, quote, random_string,\
        timestamp, to_string, get_request_url, safe_value
V = '1'
KUAIPAN_API_URL_ROOT = 'openapi.kuaipan.cn/'
REQUEST_TOKEN_BASE_URL = 'https://openapi.kuaipan.cn/open/requestToken'
ACCESS_TOKEN_BASE_URL = 'https://openapi.kuaipan.cn/open/accessToken'
AUTHORIZE_URL = 'https://www.kuaipan.cn/api.php?ac=open&op=authorise&oauth_token=%s'
ACCOUNT_INFO_BASE_URL = 'http://openapi.kuaipan.cn/1/account_info'
METADATA_BASE_URL = 'http://openapi.kuaipan.cn/1/metadata/%s/%s'
SHARE_BASE_URL = 'http://openapi.kuaipan.cn/1/shares/%s/%s'
FILEOPS_BASE_URL = 'http://openapi.kuaipan.cn/1/fileops/'
FILEOPS_CREATE_BASE_URL = FILEOPS_BASE_URL + 'create_folder'
FILEOPS_DELETE_BASE_URL = FILEOPS_BASE_URL + 'delete'
FILEOPS_MOVE_BASE_URL = FILEOPS_BASE_URL + 'move'
FILEOPS_COPY_BASE_URL = FILEOPS_BASE_URL + 'copy'
FILEOPS_DOWNLOAD_BASE_URL =  'http://api-content.dfs.kuaipan.cn/1/fileops/download_file'
FILEOPS_UPLOAD_LOCATE_BASE_URL =  'http://api-content.dfs.kuaipan.cn/1/fileops/upload_locate'


class OpenAPIError(Exception):
    pass

class OpenAPIHTTPError(OpenAPIError):
    def __init__(self, status, msg):
        self.status = status
        self.msg = msg
    def __str__(self):
        return "%s - %s" % (self.status, self.msg)

class OpenAPIArgumentError(OpenAPIError):
    pass


class kpOpenAPI(object):

    VERSION = "1.0"
    SIG_METHOD = "HMAC-SHA1"

    def __init__(self, consumer_key, consumer_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

    def requestToken(self, callback=None):
        parameters = self._oauth_parameter(has_token=False)
        if callback:
            parameters['oauth_callback'] =  callback
        base_url = REQUEST_TOKEN_BASE_URL

        s = self._sig_request_url(base_url, parameters)

        rf = urllib.urlopen(s)
        status = rf.getcode()
        if status == 200:
            d = json.loads(rf.read())
            for k in (u"oauth_token",
                        u"oauth_token_secret",
                        u"oauth_callback_confirmed"):
                if d.has_key(k):
                    v = d.get(k)
                    setattr(self, to_string(k), safe_value(v))
        else:
            raise OpenAPIHTTPError(status, rf.read())


    def authorize(self):
        s = AUTHORIZE_URL % self.oauth_token
        return s

    def accessToken(self):
        parameters = self._oauth_parameter()
        base_url = ACCESS_TOKEN_BASE_URL

        s = self._sig_request_url(base_url, parameters)

        rf = urllib.urlopen(s)
        status = rf.getcode()
        if status == 200:
            d = json.loads(rf.read())
            for k in (u"oauth_token",
                        u"oauth_token_secret",
                        u"user_id",
                        u"charged_dir"):
                if d.has_key(k):
                    v = d.get(k)
                    setattr(self, to_string(k), safe_value(v))
        else:
            raise OpenAPIHTTPError(status, rf.read())


    def account_info(self):
        parameters = self._oauth_parameter()
        base_url = ACCOUNT_INFO_BASE_URL

        s = self._sig_request_url(base_url, parameters)

        rf = urllib.urlopen(s)
        status = rf.getcode()
        if status == 200:
            d = json.loads(rf.read())
            for k in (u"max_file_size",
                        u"user_name",
                        u"user_id",
                        u"quota_total",
                        u"quota_used",
                        u"quota_recycled"):
                if d.has_key(k):
                    v = d.get(k)
                    setattr(self, to_string(k), safe_value(v))
        else:
            raise OpenAPIHTTPError(status, rf.read())

    def metadata(self, **kwargs):
        parameters = self._oauth_parameter()
        if not kwargs.get('list', True):
            parameters['list'] = False
        if kwargs.get('file_limit', 10000) < 10000:
            parameters['list'] = kwargs['file_limit']
        if kwargs.get('page', 0):
            parameters['list'] = kwargs['page']
            if kwargs.get('page_size', 20) != 20:
                parameters['page_size'] = kwargs['page_size']
        if kwargs.has_key('filter_ext'):
            parameters['filter_ext'] = kwargs['filter_ext']
        if kwargs.get('sort_by', '') and (
                kwargs['sort_by'] in ('time', 'rtime', 'name', 'rname', 'size', 'rsize')):
            parameters['sort_by'] = kwargs['sort_by']

        root = kwargs.get('root', 'app_folder')
        path = quote(kwargs.get('path', ''))

        base_url = METADATA_BASE_URL % (root, path)

        s = self._sig_request_url(base_url, parameters)

        rf = urllib.urlopen(s)
        status = rf.getcode()
        if status == 200:
            js = rf.read()
            return js
        else:
            raise OpenAPIHTTPError(status, rf.read())


    def shares(self, path, root='app_folder'):
        parameters = self._oauth_parameter()

        if root not in ('app_folder', 'kuaipan'):
            root = 'app_folder'
        path = quote(path)

        base_url = SHARE_BASE_URL % (root, path)

        s = self._sig_request_url(base_url, parameters)

        rf = urllib.urlopen(s)
        status = rf.getcode()
        if status == 200:
            d = json.loads(rf.read())
            return to_string(d[u'url'])
        else:
            raise OpenAPIHTTPError(status, rf.read())

    def create_folder(self, path, root='app_folder'):
        if root not in ('app_folder', 'kuaipan'):
            root = 'app_folder'
        if type(path) not in (str, unicode) or not path :
            raise OpenAPIArgumentError

        parameters = self._oauth_parameter()
        parameters['root'] = root
        parameters['path'] = to_string(path)

        base_url = FILEOPS_CREATE_BASE_URL

        s = self._sig_request_url(base_url, parameters)

        rf = urllib.urlopen(s)
        status = rf.getcode()
        if status == 200:
            js = rf.read()
            return js
        else:
            raise OpenAPIHTTPError(status, rf.read())

    def delete(self, path, root='app_folder', to_recycle=True):
        if root not in ('app_folder', 'kuaipan'):
            root = 'app_folder'
        if type(path) not in (str, unicode) or not path:
            raise OpenAPIArgumentError

        parameters = self._oauth_parameter()
        parameters['root'] = root
        parameters['path'] = to_string(path)
        if not to_recycle:
            parameters['to_recycle'] = False

        base_url = FILEOPS_DELETE_BASE_URL

        s = self._sig_request_url(base_url, parameters)

        rf = urllib.urlopen(s)
        status = rf.getcode()
        if status == 200:
            return True
        else:
            raise OpenAPIHTTPError(status, rf.read())

    def move(self, from_path, to_path, root='app_folder'):
        if root not in ('app_folder', 'kuaipan'):
            root = 'app_folder'
        if type(from_path) not in (str, unicode) or not from_path:
            raise OpenAPIArgumentError
        if type(from_path) not in (str, unicode) or not to_path:
            raise OpenAPIArgumentError

        parameters = self._oauth_parameter()
        parameters['root'] = root
        parameters['from_path'] = to_string(from_path)
        parameters['to_path'] = to_string(to_path)

        base_url = FILEOPS_MOVE_BASE_URL

        s = self._sig_request_url(base_url, parameters)

        rf = urllib.urlopen(s)
        status = rf.getcode()
        if status == 200:
            return True
        else:
            raise OpenAPIHTTPError(status, rf.read())

    def copy(self, from_path, to_path, root='app_folder'):
        if root not in ('app_folder', 'kuaipan'):
            root = 'app_folder'
        if type(from_path) not in (str, unicode) or not from_path:
            raise OpenAPIArgumentError
        if type(from_path) not in (str, unicode) or not to_path:
            raise OpenAPIArgumentError

        parameters = self._oauth_parameter()
        parameters['root'] = root
        parameters['from_path'] = to_string(from_path)
        parameters['to_path'] = to_string(to_path)

        base_url = FILEOPS_COPY_BASE_URL

        s = self._sig_request_url(base_url, parameters)

        rf = urllib.urlopen(s)
        status = rf.getcode()
        if status == 200:
            d = json.loads(rf.read())
            return to_string(d[u'file_id'])
        else:
            raise OpenAPIHTTPError(status, rf.read())

    def upload_locate(self, source_ip=None):
        parameters = self._oauth_parameter()
        if source_ip:
            parameters['source_ip'] = source_ip

        base_url = FILEOPS_UPLOAD_LOCATE_BASE_URL

        s = self._sig_request_url(base_url, parameters)

        rf = urllib.urlopen(s)
        status = rf.getcode()
        if status == 200:
            d = json.loads(rf.read())
            return to_string(d[u'url'])
        else:
            raise OpenAPIHTTPError(status, rf.read())

    def upload_file(self, path, overwrite=True, root='app_folder'):
        if root not in ('app_folder', 'kuaipan'):
            root = 'app_folder'
        if type(path) not in (str, unicode) or not path:
            raise OpenAPIArgumentError

        parameters = self._oauth_parameter()
        parameters['overwrite'] = overwrite
        parameters['root'] = root
        parameters['path'] = to_string(path)

        base_url = self.upload_locate() + '/1/fileops/upload_file'

        s = self._sig_request_url(base_url, parameters, 'post')
        return s

    def download_file(self, path, root='app_folder', rev=''):
        if root not in ('app_folder', 'kuaipan'):
            root = 'app_folder'
        if type(path) not in (str, unicode) or not path:
            raise OpenAPIArgumentError

        parameters = self._oauth_parameter()
        parameters['root'] = root
        parameters['path'] = path

        base_url = FILEOPS_DOWNLOAD_BASE_URL

        s = self._sig_request_url(base_url, parameters)
        return s

    def _oauth_parameter(self, has_token=True):
        parameters = {
                'oauth_consumer_key' : self.consumer_key,
                'oauth_timestamp' : timestamp(),
                'oauth_nonce' : random_string(),
                'oauth_signature_method' : self.SIG_METHOD,
                'oauth_version' : self.VERSION,
        }
        if has_token:
            parameters['oauth_token'] = self.oauth_token
        return parameters

    def _secret_key(self, has_token=True):
        s = self.consumer_secret + '&'
        if has_token:
            s += self.oauth_token_secret
        return s

    def _sig_request_url(self, base, p, method='get'):
        has_token = True if p.has_key('oauth_token') else False
        oauth_signature = generate_signature(base,
                p, self._secret_key(has_token=has_token), method)
        return get_request_url(base, p, oauth_signature)
