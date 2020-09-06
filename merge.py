# Solve audio and video out of sync problem
#
# This tool will trim the starting section of the longer mp4 file because they should always end at the same time.
# After trimming, this tool will concat audio & video.
# e.g. (after running dl_hls.py)
# output_1.mp4 (audio & video, but only need audio)
# output_2.mp4 (video only, no audio)

import os
import subprocess


curr_path = os.getcwd()

curr_dir_files = os.listdir(curr_path)
mp4_files = []
for item in curr_dir_files:
    if item.split(".")[-1] == "mp4":
        mp4_files.append(item)

mp4_files.sort()

# https://stackoverflow.com/questions/3844430/how-to-get-the-duration-of-a-video-in-python
def get_duration(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)


for idx in range(len(mp4_files) // 2):
    print(f"Merging {mp4_files[2*idx]} (Audio) with {mp4_files[2*idx+1]} (video)")
    audio_duration = get_duration(mp4_files[2*idx])
    video_duration = get_duration(mp4_files[2*idx+1])
    trim_mp4 = None
    trim_time = None
    if video_duration > audio_duration:
        trim_type = "video"
        trim_mp4 = mp4_files[2*idx+1]
        trim_time = video_duration - audio_duration
        trim_output = mp4_files[2*idx+1].split(".")[0] + "_trim" + ".mp4"
    else:
        trim_type = "audio"
        trim_mp4 = mp4_files[2*idx]
        trim_time = audio_duration - video_duration
        trim_output = mp4_files[2*idx].split(".")[0] + "_trim" + ".mp4"
    ret = os.system(f"ffmpeg -i '{trim_mp4}' -ss '{trim_time}' -c copy '{trim_output}'")

    video = mp4_files[2*idx+1]
    audio = mp4_files[2*idx]
    if trim_type == "video":
        video = trim_output
    if trim_type == "audio":
        audio = trim_output
    ret = os.system(f"ffmpeg -i '{video}' -i '{audio}' -map 0:v -map 1:a -c copy -shortest '{mp4_files[2*idx][:-6]}.mp4'")
    # 如果返回值不是0，代表非正常退出
    if ret:
        raise Exception("[merge_mp4] ffmpeg ERROR!")