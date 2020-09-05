import requests
import shutil
import time
import sys
import os
import re

class Downloader():
    def __init__(self):
        # 加载用户配置
        self.config()
        self.output_name_orig = "output"
        self.hls_url = ""
        # 最后一个.ts文件的index
        self.max_cnt = 0
        # 分辨率选择（数字越小，分辨率越高）
        self.resolution_idx = 0
        self.curr_path = os.getcwd()
        self.temp_folder = "temp_1"
        self.temp_path = os.path.join(self.curr_path, self.temp_folder)
        # 并行下载的顺序
        self.concurrent_idx = 1
        # 并行下载防止互相覆盖临时文件
        for idx in range(2, 100):
            if os.path.exists(self.temp_path):
                self.temp_folder = "temp_" + str(idx)
                self.temp_path = os.path.join(self.curr_path, self.temp_folder)
                self.concurrent_idx = idx
            else:
                break

    def config(self):
        # 是否默认执行merge_mp4()
        # "enable" = 每次都执行
        # "disable" = 每次都不执行
        self.merge_mp4_default = "disable"
    
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
            
            print(f"{self.temp_folder}/{filename} done!")


    def concat_ts(self):
        # 并行output防止互相覆盖
        filelist_name = f"filelist_{self.concurrent_idx}"
        self.output_name = self.output_name_orig + f"_{self.concurrent_idx}"

        print(f"Concat ts -> {self.output_name}")

        with open(os.path.join(self.temp_path, filelist_name), "w") as f:
            for idx in range(self.max_cnt):
                filename = f"{str(idx).zfill(5)}.ts"
                f.write(f"file '{filename}'\n")
        
        ret = os.system(f"ffmpeg -f concat -i '{os.path.join(self.temp_path, filelist_name)}' -c copy '{self.output_name}'.mp4")
        # 如果返回值不是0，代表非正常退出
        if ret:
            raise Exception("[concat_ts] ffmpeg ERROR!")

    # 可选步骤，如果下载拿到的是两个音画分离的mp4，就需要进行合并
    def merge_mp4(self):
        def call_ffmpeg(self, mp4_files):
            print(f"Merging {mp4_files[0]} (Audio) with {mp4_files[1]} (video)")
            ret = os.system(f"ffmpeg -i '{mp4_files[1]}' -i '{mp4_files[0]}' -map 0:v -map 1:a -c copy -shortest '{self.output_name_orig}.mp4'")
            # 如果返回值不是0，代表非正常退出
            if ret:
                raise Exception("[merge_mp4] ffmpeg ERROR!")
        
        if self.merge_mp4_default != "disable":
            curr_dir_files = os.listdir(self.curr_path)
            mp4_files = []
            for item in curr_dir_files:
                if item.split(".")[-1] == "mp4":
                    if self.output_name_orig in item.split(".")[0]:
                        mp4_files.append(item)
            
            if len(mp4_files) == 2:
                mp4_files.sort()
                if self.merge_mp4_default == "enable":
                    call_ffmpeg(self, mp4_files)
                else:
                    print("invalid merge_mp4_default!")


    def clean_up(self):
        shutil.rmtree(self.temp_path)

    def get_video(self, filename, hls_url):
        self.hls_url = hls_url
        self.output_name_orig = filename
        self.parse_master_m3u8()
        self.parse_index_m3u8()
        self.download_ts()
        self.concat_ts()
        self.merge_mp4()
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