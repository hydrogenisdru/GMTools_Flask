s = "/Users/zouyang/Desktop/redis_data/unzip_folder/IOS_Online_Test_Configs"
full_path = s + '/NoticeBoardDescData.json'

import hashlib


def get_md5(ct):
    md5 = hashlib.md5()
    md5.update(ct)
    return md5.hexdigest()


with open(full_path, 'r') as f:
    m = get_md5(f.read())
    print m
