# coding: utf-8
from oauth import OpenAPIOauth
import re
import urllib

username = '' # your login username
userpwd = ''  # your login password
consumer_key = '' # your consumer_key
consumer_secret = '' # your consumer_secret

root = "app_folder"
path = u'headfirstjava笔记.txt'
app_name = '同步vimwiki'
from_path = path
to_path = u'java学习笔记.txt'
url = 'https://www.kuaipan.cn/api.php?ac=open&op=authorisecheck'

a = OpenAPIOauth(consumer_key, consumer_secret)
a.requestToken()
# print '-----requstToken-----'
s = a.authorize()
s = urllib.urlopen(s).read()
m = re.search(r'oauth_token" value="(.*)"', s)
q = {'oauth_token' : m.group(1),
'app_name' : app_name,
'username' : username,
'userpwd' : userpwd,
}
urllib.urlopen(url, urllib.urlencode(q)).read()
# print '-----authorized-----'
a.accessToken()
# print '-----accessToken----'
# print a.consumer_key,a.consumer_secret, a.oauth_token, a.oauth_token_secret
# a.account_info()
# print a.max_file_size
# print "username " + a.user_name
# print a.user_id
# print a.quota_total
# print a.quota_used
# print "file " + path.encode('utf-8') + " " + a.metadata(path=path)
# print a.shares(path=path)
# print a.fileops_copy(root, from_path, to_path)
# if a.fileops_delete(root, path, to_recycle=False):
    # print "delete " + path.encode('utf-8')
# if a.fileops_move(root, to_path, from_path):
    # print "move " + to_path.encode('utf-8') + ' to ' + from_path.encode('utf-8')
# print a.fileops_download_file(path=path)
# print a.fileops_create_folder('test.py')
# print a.fileops_upload_locate()
# print a.fileops_upload_file('test.py')
