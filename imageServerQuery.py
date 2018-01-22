import requests

IMAGE_SERVER_URL = u"http://qs000.qs2.firevale.com/i"


def check_image(uuid):
    url = '%s/%s/%s' % (IMAGE_SERVER_URL, u'check', str(uuid).encode('utf8'))
    r = requests.get(url)
    if r.status_code == 200:
        return r.text
    else:
        return ''
