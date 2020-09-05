import requests
import shutil
import time
import sys
import os
import re

class Downloader():
    def __init__(self):
        self.output_name = "output"
        self.max_cnt = 0
        self.hls_url = ""
        self.resolution_idx = 0
        self.curr_path = os.getcwd()
        self.temp_path = os.path.join(self.curr_path, "temp")

    def parse_index_m3u8(self):
        if self.resolution_idx > len(self.resolution) - 1:
            self.resolution_idx = 0
        print(f"# Selected Resolution: {self.resolution[self.resolution_idx][0]}")
        resolution_info = self.resolution[self.resolution_idx][1]
        self.resolution_url_code = resolution_info.split("/")[0]
        url = self.hls_url + "/" + resolution_info
        res = requests.get(url)
        # 处理CRLF（\r\n）和LF（\n）
        content_str = res.content.decode("utf-8").replace("\r\n", "\n")
        content_lst = content_str.split("\n")
        for idx in range(1, len(content_lst)):
            if content_lst[-idx] == "#EXT-X-ENDLIST":
                last_ts_file = content_lst[-(idx+1)]
                self.max_cnt = int(last_ts_file.split(".")[0]) + 1
                break
        

    def parse_master_m3u8(self):
        self.resolution = []
        resolution_pattern = re.compile("RESOLUTION=[0-9x]+")
        url = self.hls_url + "/master.m3u8"
        res = requests.get(url)
        # 处理CRLF（\r\n）和LF（\n）
        content_str = res.content.decode("utf-8").replace("\r\n", "\n")
        content_lst = content_str.split("\n")
        content_lst = content_lst[1:-1]
        for idx in range(len(content_lst)):
            if idx % 2 == 0:
                curr_resolution = re.search(resolution_pattern, content_lst[idx])
                self.resolution.append([curr_resolution[0], content_lst[idx+1]])
        print("# Avaliable Resolution:")
        print(self.resolution)

    
    def download_ts(self):
        if not os.path.exists(self.temp_path):
            os.mkdir(self.temp_path)

        url_base = self.hls_url + "/" + self.resolution_url_code + "/"
        for idx in range(self.max_cnt):
            filename = f"{str(idx).zfill(5)}.ts"
            url = url_base + filename
            
            with open(os.path.join(self.temp_path, filename), "wb") as f:
                res = requests.get(url)
                f.write(res.content)
            
            print(f"temp/{filename} done!")


    def concat_ts(self):
        with open(os.path.join(self.temp_path, "filelist.txt"), "w") as f:
            for idx in range(self.max_cnt):
                filename = f"{str(idx).zfill(5)}.ts"
                f.write(f"file '{filename}'\n")
        
        ret = os.system(f"ffmpeg -f concat -i '{os.path.join(self.temp_path, 'filelist.txt')}' -c copy '{self.output_name}'.mp4")
        # 如果返回值不是0，代表非正常退出
        if ret:
            raise Exception("ffmpeg ERROR!")


    def clean_up(self):
        shutil.rmtree("temp")

    def get_video(self, filename, hls_url):
        self.hls_url = hls_url
        self.output_name = filename
        self.parse_master_m3u8()
        self.parse_index_m3u8()
        self.download_ts()
        self.concat_ts()
        self.clean_up()



args = sys.argv[1:]
if len(args) != 2:
    print(f"Wrong args: {args}")
    print("Usage: python dl_hls.py <FILENAME> <HLS_URL>")

filename, url = args
print(f"filename = {filename}")
print(f"URL = {url}")

dl = Downloader()
dl.get_video(filename, url)