#
# This script scrapes roms from archive.org and downloads them to a local directory.
#
# Usage: python main.py
#

import requests as http
from clint.textui import progress
import os

# extensions to search for
gc_ext = '.iso'
psx_ext = '.chd'

# set the destination directory. If the user supplied ROMS_DIR in the environment, use that.
# Otherwise, use ~/Downloads/roms
dest = os.environ.get('ROMS_DIR', os.path.join(
    os.path.expanduser('~'), 'Downloads', 'roms'))

# create the destination directory if it doesn't exist
if not os.path.exists(dest):
    os.makedirs(dest)

# th# the urls to scrape
urls = {
    'gc': [
        'https://archive.org/download/RedumpNintendoGameCubeAmerica',
        'https://archive.org/download/RedumpNintendoGameCubeAmericaPart2',
        'https://archive.org/download/RedumpNintendoGameCubeAmericaPart3'
    ],
    'psx': [
        'https://archive.org/download/chd_psx/CHD-PSX-USA/'
    ]
}

# iterate over the urls
for system, urls in urls.items():
    print(f'Processing {system}...')
    # create the system directory if it doesn't exist
    system_dir = os.path.join(dest, system)
    if not os.path.exists(system_dir):
        os.makedirs(system_dir)
    # iterate over the urls
    for url in urls:
        print(f'  {url}')
        # get the html
        html = http.get(url).text
        # extract all hrefs that end with .iso
        for href in html.split('href="')[1:]:
            href = href.split('"')[0]
            if href.endswith('.chd'):
                download_url = f'{url}{href}'
                print(f'    {download_url}')
                # create the filename from the url
                filename = href.split('/')[-1]
                # url decode the filename
                filename = http.utils.unquote(filename)
                print(filename)
                # check if the file already exists
                if not os.path.exists(f'{dest}/{system}/{filename}'):
                    # download the file to dest
                    req = http.get(download_url, stream=True)
                    with open(f'{dest}/{system}/{filename}', 'wb') as f:
                        total_length = int(req.headers.get('content-length'))
                        # display the download progress
                        for chunk in progress.bar(req.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1):
                            if chunk:
                                f.write(chunk)
                                f.flush()
