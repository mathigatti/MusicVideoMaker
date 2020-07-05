# MusicVideoMaker
Automatically generating a music video by extracting scenes from another video.

[![IMAGE ALT TEXT HERE](https://i.ytimg.com/vi/tDi7jL-jiu4/maxresdefault.jpg)](https://youtu.be/tDi7jL-jiu4)

## Requirements

- Python 3.6 or newer
- A few python libraries (Try something like `pip install -r requirements.txt`)

## How it works

### Step 1: Extracting scenes from a video

If the video contains music (i.e it's a music video) the program is going to take advantage of that identifying sections like verse, chorus and bridges, those sections are saved into temp folder, then scendetect splits those into scenes and saves the result into the scenes folder.

The script has 3 parameters. `VIDEO_PATH`, is the video we want to process. `SCENE_SPLITTER_SENSITIVITY` is an optional `integer` value, it's to tune the sensitivity of the [scene splitter](https://pyscenedetect.readthedocs.io/en/latest/examples/usage-example/), it's 20 by default. `IS_MUSIC_VIDEO` is an optional `boolean` value, it's True by default.

python scenes_preprocessing.py VIDEO_PATH SCENE_SPLITTER_SENSITIVITY IS_MUSIC_VIDEO

#### Using it over the sample file looks like this

`python scenes_preprocessing.py samples/MidnightCity.mp4`

This will generate folders containing the clips inside the _scenes_ folder.

### Step 2: Check everything is fine

It might be good before generating the final video to check that the scenes to will be used look fine. You can delete any clip that you don't like. You can also just mix or delete section folders.

### Step 3: Using scenes to create music video

Once we have our folder with video scenes we use it to create a music video. The program first idenfifies the song sections, and calls them "A", "B", "C", ... which map to the folders that contain the scenes. Then it identifies the rhythm of the song and changes of scene on every bar.

`python music_video.py PATH_TOFOLDER_WHERE_SCENES_ARE PATH_TO_SONG`

#### Using it over the sample file looks like this

`python music_video.py scenes samples/TimeToPretend.mp3`

This will generate a video called _output_
