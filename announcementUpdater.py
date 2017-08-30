from qcloud_cos import CosClient, cos_auth
import time
import urllib, hashlib
from requests_toolbelt.multipart.encoder import MultipartEncoder
import requests
import demjson
import binascii, base64
import hmac
import random
import sys


class AnnouncementUpdater:
    UPLOAD_URL = 'http://sh.file.myqcloud.com/files/v2'
    UPLOAD_HOST = 'sh.file.myqcloud.com'
    CDN_HOST = 'cdn.api.qcloud.com'
    CDN_URI = '/v2/index.php'
    UPLOAD_FOLDER = '/announcement/'
    FILE_NAME = 'NoticeBoardDescData.json'
    REFRESH_URL = 'http://biubiubiu-1252726230.file.myqcloud.com/announcement/NoticeBoardDescData.json'
    MIME_TYPE = 'application/json'
    REGION_INFO = "sh"
    APP_ID = 1252726230
    BUCKET = u'biubiubiu'
    SECRET_ID = u'AKIDTp0znOY01wfCYjhVDmBHGIE1c1EFuf7N'
    SECRET_KEY = u'BAxhFblkX8WjjXBcrxrZ5PWTFpDSWN6f'

    def __init__(self):
        self.cos_client = CosClient(self.APP_ID, self.SECRET_ID,
                                    self.SECRET_KEY,
                                    region=self.REGION_INFO)
        self.cos_path = self.UPLOAD_FOLDER + self.FILE_NAME

    def get_file(self):
        resp = requests.get(self.REFRESH_URL)
        if resp.status_code == 200:
            return resp.text
        else:
            return ''

    def update(self, filecontent):
        request_url = self.build_url(AnnouncementUpdater.UPLOAD_URL, self.cos_client.get_cred().get_appid(),
                                     self.BUCKET, self.cos_path)
        m = MultipartEncoder(
            fields={
                'op': 'upload',
                'filecontent': (self.FILE_NAME, filecontent, self.MIME_TYPE),
                'sha': self.get_sha(filecontent.read()),
                'biz_attr': '',
                'insertOnly': '0'
            })

        headers = {'Content-Type': m.content_type, 'Authorization': self.sign(),
                   'Host': self.UPLOAD_HOST, 'Content-Length': str(m.len)}

        upload_resp = requests.post(request_url, data=m, headers=headers)

        if upload_resp.status_code == 200:
            result = demjson.decode(upload_resp.text)
            if result['code'] == 0:
                return self.refreshCdnDir()
        return False

    def refreshCdnDir(self):
        params = {
            'Action': 'RefreshCdnUrl',
            'SecretId': self.SECRET_ID,
            'Timestamp': int(time.time()),
            'Nonce': random.randint(1, sys.maxint),
            'urls.0': self.REFRESH_URL
        }
        sign = self.cdn_sign_make(params=params)
        params['Signature'] = sign
        url = 'https://%s%s' % (self.CDN_HOST, self.CDN_URI)
        refresh_resp = requests.get(url, params=params, verify=False)
        if refresh_resp.status_code == 200:
            result = demjson.decode(refresh_resp.text)
            if result['code'] == 0:
                return True
        return False

    def sign(self):
        auth = cos_auth.Auth(self.cos_client.get_cred())
        expired = int(time.time()) + 999
        return auth.sign_more(self.BUCKET, urllib.quote(self.cos_path.encode('utf8'), '~/'), expired)

    def build_url(self, base_url, appid, bucket, cos_path):
        bucket = bucket.encode('utf8')
        end_point = base_url.encode('utf8')
        cos_path = urllib.quote(cos_path.encode('utf8'), '~/')
        url = '%s/%s/%s%s' % (end_point, appid, bucket, cos_path)
        return url

    def get_sha(self, content):
        sha1_obj = hashlib.sha1()
        sha1_obj.update(content)
        return sha1_obj.hexdigest()

    def cdn_sign_make(self, params, method='GET'):
        srcStr = method.upper() + self.CDN_HOST + self.CDN_URI + '?' + "&".join(
            k.replace("_", ".") + "=" + str(params[k]) for k in sorted(params.keys()))
        hashed = hmac.new(str(self.SECRET_KEY), srcStr, hashlib.sha1)
        # return binascii.b2a_base64(hashed.digest())[:-1]
        return base64.b64encode(hashed.digest())
