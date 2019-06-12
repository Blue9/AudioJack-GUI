![AudioJack-GUI](/logo/logo.png)

A smart YouTube-to-MP3 converter that automatically finds and adds ID3 tags (artist, title, album, cover art) to downloaded MP3 files.

## Disclaimer
This program is strictly intended for demonstration purposes. Using this program to download online media may breach the corresponding website's terms of service and may even be illegal in your country. Use this program at your own discretion.

## Screenshots
![AudioJack-GUI in action](/screenshots/scr_2.png)

## Step-by-step guide
This short guide will show you how to get the source version of the program up and running.

1. Install Python 3.6+.
2. Install Kivy by following the guide [here](https://kivy.org/docs/installation/installation.html#stable-version).
3. Open Command Prompt (or Terminal, depending on your OS).
4. Type in the following command: `pip install mutagen musicbrainzngs youtube_dl pyperclip validators Pillow`.
5. Download [AudioJack-GUI](https://github.com/Blue9/AudioJack-GUI/archive/master.zip) extract the files.
6. Download [`audiojack.py`](https://github.com/Blue9/AudioJack/blob/master/audiojack.py) and place it in the `AudioJack-GUI` folder.
7. Download [FFmpeg](https://ffmpeg.org/download.html) and place the files `ffmpeg`, `ffprobe`, and `ffplay` in the same folder.
8. Navigate Command Prompt to the folder and run `python launcher.py`.

Whenever you want to run the program, just repeat step 8.

## Usage
After installing necessary requirements, using the program is quite self-explanatory.

0. Run `python launcher.py`.
![Step 0](/screenshots/scr_0.png)
1. Press F1 to change the settings such as the download path for the MP3s. (optional)
![Step 1](/screenshots/scr_1.png)
2. Enter a YouTube or SoundCloud URL in the input box and wait for the results to load.
![Step 2](/screenshots/scr_2.png)
3. Select the tags that correspond to your song.
![Step 3](/screenshots/scr_2.png)
4. Voilà! The MP3 file is now downloaded. You can trim the file if you wish (this is useful if you are converting a music video).
![Step 4](/screenshots/scr_3.png)

## Requirements
1. Python 3.6+ (**not Python 2**)
2. [AudioJack](https://github.com/Blue9/AudioJack)
3. [FFmpeg](https://www.ffmpeg.org/) (for MP3 conversion).  
4. In addition, you will need to install the following modules for AudioJack to work:
 - [mutagen](https://bitbucket.org/lazka/mutagen)
 - [musicbrainzngs v0.6](https://github.com/alastair/python-musicbrainzngs)
 - [youtube-dl](https://github.com/rg3/youtube-dl)
 - [pyperclip](https://github.com/asweigart/pyperclip)
 - [validators](https://validators.readthedocs.io/en/latest/)
 - [Pillow](https://pillow.readthedocs.io)
 - [Kivy](https://kivy.org/doc/stable/gettingstarted/installation.html)

## Contribution:
- Contributing to this project is highly encouraged.

### Guidelines:
1. Use single-quotes for string literals.
2. If you use any additional modules, please update the [requirements](#requirements) if necessary.
3. Thoroughly test the program before pushing.

## Credits:
- Hoverable button functionality: [link](https://gist.github.com/opqopq/15c707dc4cffc2b6455f) (modified)
- Loading album art image: [link](https://commons.wikimedia.org/wiki/File:No-album-art.png)
