from qcloud_cos import CosClient, cos_auth, CreateFolderRequest, ListFolderRequest, UploadFileRequest
import time
import urllib, hashlib
from requests_toolbelt.multipart.encoder import MultipartEncoder
import requests
import demjson
import binascii, base64
import hmac
import random
import sys


class CdnUpdater:
    UPLOAD_URL = 'http://sh.file.myqcloud.com/files/v2'
    UPLOAD_HOST = 'sh.file.myqcloud.com'
    CDN_HOST = 'cdn.api.qcloud.com'
    CDN_URI = '/v2/index.php'
    UPLOAD_FOLDER = '/announcement/'
    FILE_NAME = 'NoticeBoardDescData.json'
    BASE_REFRESH_URL = 'http://biubiubiu-1252726230.file.myqcloud.com'
    REFRESH_URL = 'http://biubiubiu-1252726230.file.myqcloud.com/announcement/NoticeBoardDescData.json'
    MIME_TYPE = 'application/json'
    ZIP_MIME_TYPE = 'application/zip'
    REGION_INFO = "sh"
    APP_ID = 1252726230
    BUCKET = u'biubiubiu'
    SECRET_ID = u'AKIDTp0znOY01wfCYjhVDmBHGIE1c1EFuf7N'
    SECRET_KEY = u'BAxhFblkX8WjjXBcrxrZ5PWTFpDSWN6f'

    def __init__(self):
        self.cos_client = CosClient(self.APP_ID, self.SECRET_ID,
                                    self.SECRET_KEY,
                                    region=self.REGION_INFO)
        self.update_file_path = dict()
        self.refresh_url = dict()

    def set_update_file_path(self, folder_name, file_name):
        key = file_name.split('.')[0]
        self.update_file_path[key] = '/' + folder_name + '/' + file_name
        self.refresh_url[key] = self.BASE_REFRESH_URL + self.update_file_path[key]

    def check_file(self, file_name):
        key = file_name.split('.')[0]
        if self.update_file_path.has_key(key):
            return True
        else:
            return False

    def get_file(self, file_name):
        key = file_name.split('.')[0]
        if self.refresh_url.has_key(key):
            resp = requests.get(self.refresh_url[key])
            if resp.status_code == 200:
                return resp.text
            else:
                return 'bad request response'
        else:
            return 'no this file'

    def get_default_file(self):
        resp = requests.get(self.REFRESH_URL)
        if resp.status_code == 200:
            return resp.text
        else:
            return 'bad request response'

    def get_list_folder(self):
        files = self.walk_all_folders()
        # lq = ListFolderRequest(bucket_name=self.BUCKET, cos_path=u'/ClientAssets/')
        # list_folder_ret = self.cos_client.list_folder(lq)
        # if list_folder_ret['code'] == 0:
        #     return list_folder_ret['data']

    def walk_all_folders(self, walking_folders=[u"/ClientAssets/"], files_in_folder=dict()):
        try:
            next_walking_folders = []
            for walking_folder in walking_folders:
                if not isinstance(walking_folder, unicode):
                    walking_folder = unicode(walking_folder)
                files_in_folder[walking_folder] = []
                lq = ListFolderRequest(bucket_name=self.BUCKET,
                                       cos_path=walking_folder)
                list_folder_ret = self.cos_client.list_folder(lq)
                if list_folder_ret['code'] == 0 and list_folder_ret['data'] and list_folder_ret['data']['infos']:
                    for data in list_folder_ret['data']['infos']:
                        if data['name'].split('.').__len__() == 1:
                            next_walking_folders.append(walking_folder + data['name'])
                        if data['name'].split('.').__len__() == 2:
                            files_in_folder[walking_folder].append(data)
            if next_walking_folders.__len__() > 0:
                return self.walk_all_folders(walking_folders=next_walking_folders,
                                             files_in_folder=files_in_folder)
            else:
                return files_in_folder
        except Exception as e:
            print e
            return None

    def walk_folder(self, walking_folder):
        try:
            if not isinstance(walking_folder, unicode):
                walking_folder = unicode(walking_folder)
            lq = ListFolderRequest(bucket_name=self.BUCKET,
                                   cos_path=walking_folder)
            list_folder_ret = self.cos_client.list_folder(lq)
            if list_folder_ret['code'] == 0 and list_folder_ret['data'] and list_folder_ret['data']['infos']:
                for data in list_folder_ret['data']['infos']:
                    yield data
        except Exception as e:
            print e
            yield None

    def create_folder(self, cos_path):
        if not isinstance(cos_path, unicode):
            cos_path = unicode(cos_path)
        cq = CreateFolderRequest(bucket_name=self.BUCKET, cos_path=cos_path)
        cq_ret = self.cos_client.create_folder(cq)
        if cq_ret['code'] == 0:
            return True
        else:
            return False

    def upload_file(self, cos_path, local_path):
        if not isinstance(cos_path, unicode):
            cos_path = unicode(cos_path)
        if not isinstance(local_path, unicode):
            local_path = unicode(local_path)

        uq = UploadFileRequest(bucket_name=self.BUCKET, cos_path=cos_path,
                               local_path=local_path, insert_only=0)
        uq_ret = self.cos_client.upload_single_file(uq)
        if uq_ret['code'] == 0:
            return True
        else:
            return False

    def update(self, folder_name, file_name, mime_type, filecontent):
        self.set_update_file_path(folder_name, file_name)
        key = file_name.split('.')[0]
        request_url = self.build_url(CdnUpdater.UPLOAD_URL, self.cos_client.get_cred().get_appid(),
                                     self.BUCKET, self.update_file_path[key])
        m = MultipartEncoder(
            fields={
                'op': 'upload',
                'filecontent': (file_name, filecontent, mime_type),
                'sha': self.get_sha(filecontent.read()),
                'biz_attr': '',
                'insertOnly': '0'
            })

        headers = {'Content-Type': m.content_type, 'Authorization': self.sign(self.update_file_path[key]),
                   'Host': self.UPLOAD_HOST, 'Content-Length': str(m.len)}

        upload_resp = requests.post(request_url, data=m, headers=headers)

        if upload_resp.status_code == 200:
            result = demjson.decode(upload_resp.text)
            if result['code'] == 0:
                return self.refresh_cdn_url(self.refresh_url[key])
        return False

    def refresh_cdn_url(self, url):
        params = {
            'Action': 'RefreshCdnUrl',
            'SecretId': self.SECRET_ID,
            'Timestamp': int(time.time()),
            'Nonce': random.randint(1, sys.maxint),
            'urls.0': url
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

    def refresh_cdn_dir(self, folder_name):
        if folder_name[0] != '/':
            folder_name = '/' + folder_name
        url = self.BASE_REFRESH_URL + folder_name
        params = {
            'Action': 'RefreshCdnDir',
            'SecretId': self.SECRET_ID,
            'Timestamp': int(time.time()),
            'Nonce': random.randint(1, sys.maxint),
            'dirs.0': url
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

    def sign(self, cos_path):
        auth = cos_auth.Auth(self.cos_client.get_cred())
        expired = int(time.time()) + 999
        return auth.sign_more(self.BUCKET, urllib.quote(cos_path.encode('utf8'), '~/'), expired)

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
        src_str = method.upper() + self.CDN_HOST + self.CDN_URI + '?' + "&".join(
            k.replace("_", ".") + "=" + str(params[k]) for k in sorted(params.keys()))
        hashed = hmac.new(str(self.SECRET_KEY), src_str, hashlib.sha1)
        # return binascii.b2a_base64(hashed.digest())[:-1]
        return base64.b64encode(hashed.digest())
