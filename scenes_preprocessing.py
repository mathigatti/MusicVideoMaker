from moviepy.editor import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import time
from music_video import clean
import sys, os
import msaf

def parts(audio_file):
	boundaries, labels = msaf.process(audio_file, boundaries_id="foote", labels_id="fmc2d")
	parts_names = ["A","B","C","D","E","F","G","H","I","J","K","L"]
	labels2ids = {list(set(labels))[i]:parts_names[i%len(parts_names)] for i in range(len(set(labels)))}

	boundaries_info = {k:[] for k in labels2ids.values()}
	l_index = 0
	for v_min, v_max in zip(boundaries[:-1], boundaries[1:]):
		boundaries_info[labels2ids[labels[l_index]]].append((v_min,v_max))
		l_index += 1

	clean()
	return boundaries_info

def extract_audio(video,audio_path):
	video = VideoFileClip(video)
	audio = video.audio
	audio.write_audiofile(audio_path)

def extract_extension(filename):
	return filename.split(".")[-1]

def timestr():
	timestr = time.strftime("%Y%m%d-%H%M%S")
	return timestr

if __name__ == "__main__":

	video = sys.argv[1]
	if len(sys.argv) > 2:
		scenes_threshold = sys.argv[2] # https://pyscenedetect.readthedocs.io/en/latest/examples/usage-example/
	else:
		scenes_threshold = 20

	if len(sys.argv) > 3:
		music_video = bool(sys.argv[3])
	else:
		music_video = True

	timestamp = timestr()
	extension = extract_extension(video)

	if music_video:
		audio = f"temp/youtube_video_audio_{timestamp}.mp3"
		print("Extracting audio")
		extract_audio(video, audio)

		print("Identifying song sections")
		boundaries_info = parts(audio)
	else:
		boundaries_info = {"A":[(0,float('inf'))]}

	print("Splitting song based on sections")
	os.system("rm -rf temp/*")
	for part_name, boundaries in boundaries_info.items():
		os.system(f"mkdir -p temp/{part_name}")
		os.system(f"mkdir -p scenes/{part_name}")
		for v_min, v_max in boundaries:
			temp_video = f"temp/{part_name}/{timestr()}.{extension}"
			ffmpeg_extract_subclip(video, v_min, v_max, targetname=temp_video)
			os.system(f"scenedetect -q -i {temp_video} -o scenes/{part_name} detect-content -t {scenes_threshold} split-video")