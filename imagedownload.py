# -*- coding:UTF-8 -*-
import requests, json, time
from contextlib import closing

'''
if __name__ == '__main__':
     target = 'https://unsplash.com/napi/photos?page=6&per_page=12'
     download_server = 'https://unsplash.com/photos/xxx/download?force=trues'
     req = requests.get(url = target, verify = False)
     #print(req.text)
     html = json.loads(req.text)
     photos_id = []
     for ids in html:
          photos_id.append(ids['id'])

     for i in range(len(photos_id)):
          print('  正在下载第%d张图片...' % (i + 1))
          download = download_server.replace('xxx', photos_id[i])
          with closing(requests.get(url = download, verify = False)) as r:
               with open('./images/%d.jpg' % (i + 1), 'ab+') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                         if chunk:
                              f.write(chunk)
                              f.flush()
'''

class get_photos(object):

    def __init__(self):
        self.photos_id = []
        self.download_server = 'https://unsplash.com/photos/xxx/download?force=true'
        self.target = 'https://unsplash.com/napi/photos?page=xxx&per_page=12'
        self.headers = {'authorization':'Client-ID c94869b36aa272dd62dfaeefed769d4115fb3189a9d1ec88ed457207747be626'}
        self.page = 13

    """
    函数说明:获取图片ID
    """
    def get_ids(self, pagenums):
        for i in range(pagenums):
             target = self.target.replace('xxx', str(i))
             req = requests.get(url=target, verify=False)
             html = json.loads(req.text)
             for ids in html:
                  self.photos_id.append(ids['id'])
             time.sleep(1)

    """
    函数说明:图片下载
    """
    def download(self, photo_id, filename):
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'}
        target = self.download_server.replace('xxx', photo_id)
        with closing(requests.get(url=target, stream=True, verify = False)) as r:
            with open('./images/%d.jpg' % filename, 'ab+') as f:
                for chunk in r.iter_content(chunk_size = 1024):
                    if chunk:
                        f.write(chunk)
                        f.flush()


if __name__ == '__main__':
    gp = get_photos()
    print('获取图片连接中...')
    gp.get_ids(pagenums=gp.page)
    print('图片下载中...')
    for i in range(len(gp.photos_id)):
        print('正在下载第%d张图片' % (i+1))
        gp.download(gp.photos_id[i], (i+1))
