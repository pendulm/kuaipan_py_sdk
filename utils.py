import base64
import hashlib
import hmac
import random
import urllib
import string
import time

SIGNATURE_CHARACTERS = string.letters + string.digits + '_'

def random_string():
    lens = random.randint(1,31)
    s = []
    for i in range(lens):
        s.append(random.choice(SIGNATURE_CHARACTERS))
    return ''.join(s)

def quote(s):
    s = to_string(s)
    return urllib.quote(s, '~')


def generate_signature(base_uri, parameters, key, http_method='get'):
    s = ''
    s += (http_method.upper()+'&')
    s += (quote(base_uri) + '&')
    s += quote('&'.join(sorted(
        [quote(k) + "=" + quote(v) for k, v in parameters.items()])))
    s = hmac.new(key, s, hashlib.sha1).digest()
    s = base64.b64encode(s)
    s = quote(s)
    return s

def timestamp():
    return int(time.time())

def to_string(a):
    if type(a) is bool:
        s = 'true' if a else 'false'
    elif type(a) is unicode:
        s = a.encode('utf-8')
    else:
        s = str(a)
    return s

def get_request_url(base_url, parameters, signature):
    s = base_url + '?'
    s += '&'.join([to_string(k) + "=" + quote(v) for k, v in parameters.items()])
    s += '&oauth_signature=' + signature
    return s

def safe_value(v):
    if type(v) is unicode:
        return v.encode('utf-8')
    else:
        return v
