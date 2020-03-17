# -*- coding: utf-8 -*-

import subprocess, youtube_dl
import hashlib

class DownloadVideo(object):
    green = "\033[1;32;40m  %s  \033[0m"

    def rename_hook(self, d):
        if d['status'] == 'finished':
            print(self.green % 'Done Downloading!!!')
    
    def download(self,youtube_url, md5_url):
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]',
                'outtmpl':'twitter_data/images/%s.jpg'%(md5_url),
                'progress_hooks': [self.rename_hook],
                'writeautomaticsub':True,
                'subtitleslangs':'en',
                'proxy':'127.0.0.1:8118'
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                result = ydl.download([youtube_url])

    def videos_dowloader(self):
        account = open('image_url.txt', 'r')
        for i in account:
            url_md5 = hashlib.md5(u"%s".encode('utf8')% i.strip()).hexdigest()
            subprocess.call('''youtube-dl --proxy 127.0.0.1:8118 -o "twitter_data/images/%s.jpg" %s \
                --external-downloader aria2c --external-downloader-args "-x 16 -k 1M"'''%(url_md5, i.strip()), shell=True)

if __name__ == '__main__':
    obj = DownloadVideo()
    obj.videos_dowloader()
