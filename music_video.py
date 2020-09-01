from moviepy.editor import * 
import librosa
import madmom
import msaf
import sys
import os
import subprocess
import youtube_dl

def download_from_youtube(yt_url,song_name="youtube_song.mp3"):
  ydl_opts = {
      'outtmpl': song_name,
      'format': 'bestaudio/best',
      'postprocessors': [{
          'key': 'FFmpegExtractAudio',
          'preferredcodec': 'mp3',
          'preferredquality': '192',
      }],
  }

  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
      ydl.download([yt_url])

def video_length(video):
	cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {video}".split()
	output = subprocess.check_output(cmd)
	return float(output)

def clean():
	os.system("rm -rf .features_msaf_tmp.json")
	os.system("rm -rf estimations")

def not_empty(folder):
  return len(os.listdir(folder)) > 0

def parts(audio_file,videos_folder):
	os.system(f'DBNDownBeatTracker --downbeats single "{audio_file}" >> beats.txt')
	with open('beats.txt','r') as f:
		downbeat_times = list(map(float,f.readlines()))
	
	boundaries, labels = msaf.process(audio_file, boundaries_id="foote", labels_id="fmc2d")
	print("BOUNDARIES",boundaries)
	print("LABELS",labels)

	parts_names = [folder for folder in os.listdir(videos_folder) if len(folder) == 1 and not_empty(os.path.join(videos_folder,folder))]
	labels2ids = {list(set(labels))[i]:parts_names[i%len(parts_names)] for i in range(len(set(labels)))}

	boundaries_info = {k:[] for k in labels2ids.values()}
	l_index = 0
	for v_min, v_max in zip(boundaries[:-1], boundaries[1:]):
		boundaries_info[labels2ids[labels[l_index]]].append((v_min,v_max))
		l_index += 1

	start = 0.0
	end = boundaries[-1]
	downbeat_times = [start] + list(downbeat_times) + [end]
	
	clean()
	return boundaries_info, downbeat_times

def find_part(start,boundaries_info):
	for part_name, values in boundaries_info.items():
		for v_min, v_max in values:
			if v_max > start and start > v_min + 1:
				return part_name
	return "A"

def join_videos(clips, starts, audio, durations, output_name="output.mp4"):
	clips = [VideoFileClip(clips[i]).set_duration(durations[i]+1).set_start(starts[i]) for i in range(len(clips))]
	background_music = AudioFileClip(audio)
	clip = CompositeVideoClip(clips).set_audio(background_music)
	clip.write_videofile(output_name)

def video_lengths(videos_folder, parts_names):
	lengths = {}
	for part_name in parts_names:
		folder = f"{videos_folder}/{part_name}/"
		lengths[part_name] = {video: video_length(folder + video) for video in os.listdir(folder)}
	return lengths

def music_video(videos_folder,audio):
	
	boundaries_info, downbeat_times = parts(audio,videos_folder)
	parts_names = set(boundaries_info.keys())
	lengths = video_lengths(videos_folder, parts_names)

	clips = []
	durations = []

	for i in range(len(downbeat_times)-1):
		start = downbeat_times[i]
		end = downbeat_times[i+1]

		duration = end - start
		durations.append(duration)

		part_name = find_part(start,boundaries_info)

		folder = f"{videos_folder}/{part_name}/"
		#print(part_name)
		#print(lengths[part_name])
		#print(duration)
		files = list(filter(lambda video : lengths[part_name][video] >= duration+2, os.listdir(folder)))
		#print(files)
		if len(files) == 0:
			files = list(map(lambda x : x[0],sorted(zip(os.listdir(folder),lengths[part_name]),key=lambda x : x[1],reverse=True)))
			#print(files)

		n_files = len(files)

		clip = f"{videos_folder}/{part_name}/{files[i%n_files]}"
		clips.append(clip)

	join_videos(clips, downbeat_times, audio, durations)

if __name__ == "__main__":

	videos_folder = sys.argv[1]
	audio = sys.argv[2]

	if "youtube" in audio:
		download_from_youtube(audio,song_name="youtube_song.mp3")
		audio = "youtube_song.mp3"

	music_video(videos_folder,audio)
