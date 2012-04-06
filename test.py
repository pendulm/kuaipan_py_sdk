# coding: utf-8
from openapi import kpOpenAPI
import re
import urllib
import json
import os

username = '' # your login username
userpwd = ''  # your login password
consumer_key = '' # your consumer_key
consumer_secret = '' # your consumer_secret
app_name = '' # your app name don't prefix u

root = "app_folder"
path = u'测试文件1'
from_path = path
to_path = u'测试文件2'
test_dir = u'测试文件夹'
url = 'https://www.kuaipan.cn/api.php?ac=open&op=authorisecheck'

a = kpOpenAPI(consumer_key, consumer_secret)
a.requestToken()
print 'requstToken [OK]'

s = a.authorize()
s = urllib.urlopen(s).read()
m = re.search(r'oauth_token" value="(.*)"', s)
q = {'oauth_token' : m.group(1),
'app_name' : app_name,
'username' : username,
'userpwd' : userpwd,
}
urllib.urlopen(url, urllib.urlencode(q)).read()
print 'authorized [OK]'

a.accessToken()
print 'accessToken [OK]'
print "consumer_key: " + a.consumer_key
print "consumer_secret: " + a.consumer_secret
print "oauth_token: " + a.oauth_token
print "oauth_token_secret: " + a.oauth_token_secret

a.account_info()
print "username: " + a.user_name

app_folder = json.loads(a.metadata())
for f in app_folder['files']:
    if f['name'] == path:
        print "file %s exist already" % path.encode('utf-8')
        if a.delete(path):
            print "deleted %s" % path.encode('utf-8')
        break
url = a.upload_file(path)
os.system('curl "%s" -F file=@test.py > output' % url)

for f in app_folder['files']:
    if f['name'] == to_path:
        print "file %s exist already" % to_path.encode('utf-8')
        if a.delete(to_path):
            print "deleted %s" % test_dir.encode('utf-8')
        break

if a.move(from_path, to_path):
    print "move " + from_path.encode('utf-8') + ' to ' + to_path.encode('utf-8')

print a.copy(to_path, from_path)

url = a.download_file(to_path)
os.system('curl -L "%s" -o /tmp/%s > output' % (url, to_path.encode('utf-8')))
print "download %s" % to_path.encode('utf-8')

for f in app_folder['files']:
    if f['name'] == test_dir:
        print "file %s exist already" % test_dir.encode('utf-8')
        if a.delete(test_dir):
            print "deleted %s" % test_dir.encode('utf-8')
        break
print a.create_folder(test_dir)
print "create folder %s" % test_dir.encode('utf-8')

url = a.shares(path)
print "share file %s in link %s" % (path.encode('utf-8'), url)
