# AudioJack-GUI
A GUI front end for AudioJack written in Python.

## Requirements
1. Python 2.7
2. [AudioJack](https://github.com/Blue9/AudioJack)
2. [FFmpeg](https://www.ffmpeg.org/) (for MP3 conversion).  
3. In addition, you will need to install the following modules for AudioJack to work:
 - [mutagen](https://bitbucket.org/lazka/mutagen)
 - [musicbrainzngs v0.6.dev0](https://github.com/alastair/python-musicbrainzngs)
 - [youtube-dl](https://github.com/rg3/youtube-dl)

## Usage
First, you must set a user agent in the source code. This will let MusicBrainz know who is accessing their database and prevent abuse of their services.

    audiojack.set_useragent('Name', 'Version')
**Note:** Both "Name" and "Version" should be strings.
