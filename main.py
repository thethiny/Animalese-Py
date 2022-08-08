import json
import os
import random
from functools import partial
from multiprocessing.pool import ThreadPool
from sys import argv
from threading import local

import moviepy.editor as mp
from moviepy.editor import ColorClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from proglog import TqdmProgressBarLogger
from tqdm import tqdm

from consts import DATA_FOLDER, OUTPUT_FOLDER, TEXTS_FOLDER
from text_parser import parse_file
from transformations import sample_to_seconds, shift_pitch

MOVIEPY_LOGGER = TqdmProgressBarLogger(print_messages=False)
CACHING = os.environ.get("CACHING", "false").lower() == "true"
CODEC = "mp4_alt"
SHIFT_OFFSET = 6
SHIFT_AMT = 0


def mapping_to_timestamps(mapping, sample_rate):
    start = mapping["start"]
    end = mapping["length"] + start
    return sample_to_seconds(start, sample_rate), sample_to_seconds(end, sample_rate)


def get_text_video(
    mapping_data, char, input_video: VideoFileClip, speed_shift_amt, sample_rate=48000
):
    repeat, char, text_duration = char
    text_duration = text_duration * speed_shift_amt
    find_char = mapping_data.get(char, None)

    if find_char is None:
        raise Exception(f"Could not find char: {char}")

    start, end = mapping_to_timestamps(find_char, sample_rate)
    char_video = input_video.subclip(start, end)

    black_fill = ColorClip(
        size=(1, 1),
        color=(0, 0, 0),
        duration=text_duration,
    ).set_fps(15)

    if char == " ":
        # Space, just return the black fill with no audio
        return black_fill

    black_fill = black_fill.set_audio(char_video.audio)

    pitch_amt = SHIFT_AMT
    if not pitch_amt:
        return black_fill

    if SHIFT_OFFSET:
        cur_offset = SHIFT_OFFSET
        offset_extra = SHIFT_AMT / 12
        cur_offset -= abs(offset_extra * 2)
        random_pitch_offset = random.random() * cur_offset - (cur_offset / 2)
        pitch_offset = pitch_amt + random_pitch_offset
    else:
        pitch_offset = pitch_amt
    black_fill = shift_pitch(black_fill, pitch_offset)
    return black_fill


def process_char(mappings, chars, video_path, speed_shift_amt, char_idx):
    if not hasattr(shared_local, "video") or not shared_local.video:
        shared_local.video = in_video = VideoFileClip(video_path)
        shared_local.video.audio = in_video.audio.set_fps(48000)  # type: ignore
        shared_local.sample_rate = shared_local.video.audio.fps

    return get_text_video(
        mappings,
        chars[char_idx],
        shared_local.video,
        speed_shift_amt,
        shared_local.sample_rate,
    )


if __name__ == "__main__":
    if len(argv) < 3:
        print(f"Usage: python {argv[0]} <input_video> <input_script>")
        exit(1)

    if len(argv) > 3:
        SHIFT_AMT = int(argv[3])

    input_video_path = os.path.join(DATA_FOLDER, f"{argv[1]}.mp4")
    input_script_path = os.path.join(TEXTS_FOLDER, f"{argv[2]}.txt")
    mappings_path = os.path.join(DATA_FOLDER, f"{argv[1]}.json")

    with open(mappings_path, "r") as f:
        mappings = json.load(f)
        mappings[" "] = {  # Add space to mappings
            "start": 0,
            "length": 0,
        }

    script = parse_file(input_script_path)

    speed_shift_amt = 1.85
    output_path = f"{argv[2]}_{speed_shift_amt}_{argv[1]}" + ".{ext}"

    print(
        f"Task -> Actor: {argv[1].strip().title()} \n\
        Script: {argv[2].replace('_', ' ').strip().title()} \n\
        Speed Up: {speed_shift_amt} \n\
        Shift Amount: {SHIFT_AMT} \n\
        {len(script)} notes"
    )

    shared_local = local()

    videos = []
    char = -1

    pool = ThreadPool(6)
    process_char_partial = partial(
        process_char, mappings, script, input_video_path, speed_shift_amt
    )
    results = tqdm(pool.imap(process_char_partial, range(len(script))))
    videos = list(results)

    concat_clip = mp.concatenate_videoclips(videos)

    output_path_folder = os.path.join(OUTPUT_FOLDER, argv[1].strip())
    if not os.path.exists(output_path_folder):
        os.makedirs(output_path_folder)
    out_file = os.path.join(output_path_folder, output_path).replace("/", "\\")
    out_file_mp4 = out_file.format(ext="mp4")
    out_file_mp3 = out_file.format(ext="mp3")

    print("Shift Speed: {}".format(speed_shift_amt))
    concat_clip = concat_clip.speedx(speed_shift_amt)
    concat_clip.audio = concat_clip.audio.set_fps(48000)  # type: ignore

    print("===================")
    print("Saving Finished Files")
    print(f"Audio: {out_file_mp3}")
    # print(f"Video: {out_file_mp4}")
    print("Duration: {:.2f}".format(concat_clip.duration))
    print("===================")

    # Save Audio
    concat_clip.audio.write_audiofile(
        out_file_mp3,
        logger=MOVIEPY_LOGGER,
        # codec=codecs[CODEC]["audio_codec"],
    )

    print("Saving Done!")

    # # Save Video
    # concat_clip.write_videofile(
    #     out_file_mp4,
    #     codec=codecs[CODEC]["codec"],
    #     audio_codec=codecs[CODEC]["audio_codec"],
    #     logger=MOVIEPY_LOGGER,
    #     threads=6,
    # )

    try:
        os.startfile(out_file_mp3)
    except Exception:
        pass
