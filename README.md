![AudioJack-GUI](https://raw.githubusercontent.com/Blue9/AudioJack-GUI/master/logo/AudioJack%20Logo.png)

A smart YouTube-to-MP3 converter that automatically finds and adds ID3 tags (artist, title, album, cover art) to downloaded MP3 files.

- [Official website](http://blue9.github.io/AudioJack-GUI/)

- [Web version](http://www.audiojack.io/)

## Disclaimer
This program is strictly intended for demonstration purposes. Using this program to download online media may breach the corresponding website's terms of service and may even be illegal in your country. Use this program at your own discretion.

## Screenshots
![AudioJack-GUI in action](https://raw.githubusercontent.com/Blue9/AudioJack-GUI/master/screenshots/Screenshot_v2.png)

## Step-by-step guide
This short guide will show you how to get the source version of the program up and running.

1. Install [Python 2.7](https://www.python.org/download/releases/2.7/)
2. Open Command Prompt (or Terminal, depending on your OS).
3. Type in the following command: `pip install mutagen musicbrainzngs youtube_dl pyperclip validators Pillow`.
4. Download [`audiojack.py`](https://github.com/Blue9/AudioJack/blob/master/audiojack.py) and place it in a folder of your choice (you will be running the program from this folder, so I suggest you pick a folder other than your default downloads folder).
5. Download [`audiojack_gui.py`](https://github.com/Blue9/AudioJack-GUI/blob/master/audiojack_gui.py) and [`AudioJack Icon.ico`](https://github.com/Blue9/AudioJack-GUI/blob/master/AudioJack%20Icon.ico) and place them in the same folder as `audiojack.py`.
6. Download [FFmpeg](https://ffmpeg.org/download.html) and place the files `ffmpeg`, `ffprobe`, and `ffplay` in the same directory as your AudioJack files.
7. Navigate Command Prompt to the folder and run `python audiojack_gui.py`.

Whenever you want to run the program, just repeat step 7.

## Usage
After installing necessary requirements, using the program is quite self-explanatory.

1. Run `python audiojack_gui.py`.
![Step 0](https://raw.githubusercontent.com/Blue9/AudioJack-GUI/master/screenshots/AudioJack%20Steps/Step%200.png)
2. Paste a YouTube or SoundCloud URL in the search box and click on "Go!"
![Step 1](https://raw.githubusercontent.com/Blue9/AudioJack-GUI/master/screenshots/AudioJack%20Steps/Step%201.png)
3. Wait for about 10 seconds as the program loads.
![Step 2](https://raw.githubusercontent.com/Blue9/AudioJack-GUI/master/screenshots/AudioJack%20Steps/Step%202.png)
4. A grid of song titles, artists, and albums will appear.
![Step 3](https://raw.githubusercontent.com/Blue9/AudioJack-GUI/master/screenshots/AudioJack%20Steps/Step%203.png)
5. Click on the metadata you wish to add to your downloaded MP3 file, or if none of them are correct, fill out the "Custom tags" form.
![Step 4](https://raw.githubusercontent.com/Blue9/AudioJack-GUI/master/screenshots/AudioJack%20Steps/Step%204.png)
6. Voilà! The MP3 file will be in the same directory you ran the program from.
![Step 5](https://raw.githubusercontent.com/Blue9/AudioJack-GUI/master/screenshots/AudioJack%20Steps/Step%205.png)

## Requirements
1. Python 2.7
2. [AudioJack](https://github.com/Blue9/AudioJack)
2. [FFmpeg](https://www.ffmpeg.org/) (for MP3 conversion).  
3. In addition, you will need to install the following modules for AudioJack to work:
 - [mutagen](https://bitbucket.org/lazka/mutagen)
 - [musicbrainzngs v0.6](https://github.com/alastair/python-musicbrainzngs)
 - [youtube-dl](https://github.com/rg3/youtube-dl)
 - [pyperclip](https://github.com/asweigart/pyperclip)
 - [validators](https://validators.readthedocs.io/en/latest/)
 - [Pillow](https://pillow.readthedocs.io)

## Contribution:
- Contributing to this project is highly encouraged.

### Guidelines:
1. Use single-quotes for string literals.
2. If you use any additional modules, please update the [requirements](#requirements) if necessary.
3. Thoroughly test the program before pushing.

*More guidelines will be added if necessary.*

**Note:** Please only modify `audiojack_gui.py` and **not** `audiojack_gui_beta.py`. Any pull requests for `audiojack_gui_beta.py` will be rejected.
