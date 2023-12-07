import os
from glob import glob
import numpy as np
import os.path as P
import argparse
from multiprocessing import Pool
from functools import partial
import subprocess

def execCmd(cmd):
    r = os.popen(cmd)
    text = r.read()
    r.close()
    return text

def pipeline_test(audio_path, output_dir, fps, sr, duration_target):
    # audio_name = os.path.basename(audio_path)
    audio_path, audio_name = os.path.split(audio_path)
    # audio_name = video_name.replace(".mp4", ".wav")
    # Repeat Video
    # audio_path = P.join(output_dir, "audio_arb_len")
    duration = execCmd(f"ffmpeg -i {P.join(audio_path, audio_name)}  2>&1 | grep 'Duration' | cut -d ' ' -f 4 | sed s/,//")
    duration = duration.replace('\n', "")
    repeat_audio_dir = P.join(output_dir, "audio_repeat")
    os.makedirs(repeat_audio_dir, exist_ok=True)
    hour, min, sec = [float(_) for _ in duration.split(":")]
    duration_second = 3600*hour + 60*min + sec
    n_repeat = duration_target//duration_second + 1
    os.system("ffmpeg -stream_loop {} -i {} -loglevel error -c copy -fflags +genpts -y {}".format(n_repeat, 
            P.join(audio_path, audio_name), P.join(repeat_audio_dir, audio_name)))

    # Cut Video
    cut_audio_dir = P.join(output_dir, f"audio_{duration_target}s")
    os.makedirs(cut_audio_dir, exist_ok=True)
    # os.system("ffmpeg -ss 0 -t {} -i {} -loglevel error -c:v libx264 -c:a aac -strict experimental -b:a 98k -y {}".format(duration_target, 
    #         P.join(repeat_audio_dir, audio_name), P.join(cut_audio_dir, audio_name)))
    subprocess.run(["ffmpeg", "-i", os.path.join(repeat_audio_dir, audio_name), "-ss", "0", "-t", str(duration_target), "-c", "copy", os.path.join(cut_audio_dir, audio_name)])

    # change audio sample rate
    sr_audio_dir = P.join(output_dir, f"audio_{duration_target}s_{sr}hz")
    os.makedirs(sr_audio_dir, exist_ok=True)
    os.system("ffmpeg -i {} -loglevel error -ac 1 -ab 16k -ar {} -y {}".format(
            P.join(cut_audio_dir, audio_name), sr, P.join(sr_audio_dir, audio_name)))

if __name__ == '__main__':

    paser = argparse.ArgumentParser()
    paser.add_argument("-i", "--input_dir", default="data/features/dog/audio_full")
    paser.add_argument("-o", "--output_dir", default="data/features/dog")
    paser.add_argument("-d", "--duration", type=int, default=10)
    paser.add_argument("-a", '--audio_sample_rate', default='22050')
    paser.add_argument("-v", '--video_fps', default='21.5')
    paser.add_argument("-n", '--num_worker', type=int, default=32)
    args = paser.parse_args()
    input_dir = args.input_dir
    output_dir = args.output_dir
    duration_target = args.duration
    sr = args.audio_sample_rate
    fps = args.video_fps
    
    audio_paths = glob(P.join(input_dir, "*.wav"))
    audio_paths.sort()

    with Pool(args.num_worker) as p:
        p.map(partial(pipeline_test, output_dir=output_dir, 
        sr=sr, fps=fps, duration_target=duration_target), audio_paths)

