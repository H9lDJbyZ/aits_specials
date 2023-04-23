from mutagen.mp3 import MP3
import pyrogram
import feedparser
from pprint import pprint
from dotenv import load_dotenv
from os import environ, remove, path
import requests
import pickledb


if __name__=='__main__':
    load_dotenv()
    feed_url = environ.get('BOOSTY_URL')
    t_chat_id = int(environ.get('TG_CHAT_ID'))
    t_api_id = int(environ.get('TG_API_ID'))
    t_api_hash = environ.get('TG_API_HASH')
    t_app_name = environ.get('TG_APP_NAME')
    
    # print('')
    feed = feedparser.parse(feed_url)

    db = pickledb.load('example.db', False)
    all_id = db.getall()

    for entry in reversed(feed['entries']):
        id = entry['id']
        if id not in all_id:
            title = entry['title']
            print(f'NEW {title}')
            summary = entry['summary']
            url = ''
            for href in entry['links']:
                if href['rel'] == 'enclosure':
                    url = href['href']
                    length = href['length']
                    fn = f'download/{id}.mp3'
                    
                    need_download = True
                    if path.exists(fn):
                        if path.getsize(fn) == length:
                            need_download = False
                        else:
                            remove(fn)
                    if need_download:
                        print(f'Download {length}...', end='')
                        r = requests.get(url)
                        print(r.status_code)
                        if r.status_code == 200:
                            print(f'downloaded {len(r.content)}, saving...', end='')
                            with open(fn, 'wb') as f:
                                f.write(r.content)
                            print('saved')

                    audio = MP3(fn)
                    duration = int(audio.info.length)

                    print('Upload to chat...', end='')
                    app = pyrogram.Client(
                            name=t_app_name, 
                            api_id=t_api_id, 
                            api_hash=t_api_hash
                        )
                    with app:
                        app.send_audio(
                                chat_id=t_chat_id, 
                                audio=fn, 
                                title=title, 
                                caption=f'{title}\n\n{summary}',
                                duration=duration,
                            )
                    print('uploaded')

                    db.set(id, id)
                    db.dump()

                    # remove(fn)
