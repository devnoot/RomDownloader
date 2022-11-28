#
# This script scrapes roms from archive.org and downloads them to a local directory.
#
# Usage: python main.py
#

import requests as http
from clint.textui import progress
import os
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from config import config


def get_system_game_ext(system):
    if system == 'gc' or system == 'psp':
        return '.zip'
    elif system == 'psx':
        return '.chd'
    else:
        # these systems use .7z
        # nes, snes, n64, gb, gba, gbc, vb, tg-16
        return '.7z'


def download_file(url, name, dest):
    filename = url.split('/')[-1]
    filename = decode_url(filename)
    req = http.get(url, stream=True)
    print(f'Downloading {url}')
    with open(dest, 'wb') as f:
        total_length = int(req.headers.get('content-length'))
        for chunk in progress.bar(req.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1):
            if chunk:
                f.write(chunk)
                f.flush()


def create_dest():
    # set the destination directory. If the user supplied ROMS_DIR in the environment, use that.
    # Otherwise, use ~/Downloads/roms
    dest = os.environ.get('ROMS_DIR', os.path.join(
        os.path.expanduser('~'), 'Downloads', 'roms'))
    # create the destination directory if it doesn't exist
    if not os.path.exists(dest):
        os.makedirs(dest)
    return dest


def get_systems():
    return config.keys()


# decode a url string
def decode_url(url):
    return http.utils.unquote(url)


# encode a url
def encode_url(url):
    return http.utils.quote(url)

# return a list of a systems games


def get_games(system, ext):
    urls = config[system]
    games = []
    for url in urls:
        html = http.get(url).text
        for href in html.split('href="')[1:]:
            href = href.split('"')[0]
            if href.endswith(ext):
                game = href.split('/')[-1]
                games.append([system, game, url])
    return games


# create system directory if it doesn't exist


def create_system_dir(dest, system):
    system_dir = os.path.join(dest, system)
    if not os.path.exists(system_dir):
        os.makedirs(system_dir)
    return system_dir


def create_system_completer():
    # create a prompt_toolkit WordCompleter for the systems
    return WordCompleter(get_systems())


def main():

    system_completer = create_system_completer()
    system_input = prompt(
        'Enter a system (use tab for autocopmlete): ', completer=system_completer)
    print(f'Getting games for: {system_input}')

    # get the games for the system
    # Each game looks like this -> [system, game, url]
    games = get_games(system_input, get_system_game_ext(system_input))

    # extract the game names from the list
    game_names = [game[1] for game in games]
    # url decode the game names
    game_names = [decode_url(game) for game in game_names]

    # prompt the user to select a game
    game_completer = WordCompleter(game_names)
    game_input = prompt(
        'Enter a game, (a) to download all: ', completer=game_completer)

    if game_input == 'a':
        # download all games
        for game in games:
            system = game[0]
            game_name = game[1]
            url = game[2]
            dest = create_system_dir(create_dest(), system)
            download_file(f'{url}/{game_name}', game_name,
                          os.path.join(dest, decode_url(game_name)))

    # print the game the user selected
    print(f'Getting game: {game_input}')

    # get the url for the selected game
    game_url = [game[2]
                for game in games if game[1] == encode_url(game_input)][0]
    # encode the game name
    game_input = encode_url(game_input)
    # construct the download url
    download_url = f'{game_url}/{game_input}'
    # create the destination directory
    dest = create_dest()
    system_dir = create_system_dir(dest, system_input)
    # download the game
    download_file(download_url, game_input,
                  os.path.join(system_dir, game_input))
    exit()


if __name__ == '__main__':
    main()


# TODO: Prompt validate
