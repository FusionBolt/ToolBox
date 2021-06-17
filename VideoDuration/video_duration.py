import os
import logging
import cv2

log_name = 'tools.log'
logging.basicConfig(filename=log_name, filemode="a", level=logging.DEBUG)

def get_pure_file_name(absolute_path):
    return os.path.splitext(os.path.split(absolute_path)[1])[0]

def write_data(file_path, data):
    try:
        f = open(file_path, 'a')
        f.write(data)
    except Exception as e:
        logging.info("write data error:" + file_path + repr(e))
    finally:
        f.close()

# TODO: log path
def recursive_process_file(rootdir, process):
    file_list = os.listdir(rootdir)
    for i in range (0, len(file_list)):
        path = os.path.join(rootdir, file_list[i])
        if os.path.isfile(path):
            logging.info("process:" + path)
            process(path)
        if os.path.isdir(path):
            recursive_process_file(path, process)

durations = []
def get_video_info(path):
    if not path.endswith(".flv"):
        return
    cap = cv2.VideoCapture(path)
    if cap.isOpened():
        rate = cap.get(5) # 帧速率
        frameNumber = cap.get(7) # 总帧数
        duration = round(frameNumber / rate / 60, 2) # 小数点后两位
        durations.append(duration)

if __name__ == "__main__":
    rootdir = '' 
    recursive_process_file(rootdir, get_video_info)
    print("sum minute", sum(durations))
    print("sum hour", sum(durations) / 60)