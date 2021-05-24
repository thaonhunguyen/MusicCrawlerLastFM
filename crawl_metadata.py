import os
import os.path as osp
from models import *
import requests
from bs4 import BeautifulSoup
from collections import defaultdict


# Define some constants here
BASE_URL = 'https://www.last.fm'
START_URL = 'https://www.last.fm/user/cgurrin/library' # base url
MAX_PAGE_NUMBER = 655 # adjust max page number to fit the maximum crawling page of each person

start_urls = [f'{START_URL}?page={page_no}' for page_no in range(1, MAX_PAGE_NUMBER+1)]

def parse_track_info(response: str, track_url: str = None) -> TrackModel:
    # Initial beautifulsoup object, read form response
    soup = BeautifulSoup(response, 'html.parser')
    artist_name = soup.find('a', class_='header-new-crumb').find('span').text
    track_name = soup.find('h1', class_='header-new-title').text
    track_length = soup.find('dd', class_='catalogue-metadata-description').text.strip()
    album_name = soup.find('h4', class_='source-album-name').find('a').text
    
    similar_tracks, track_tags = [], []
    
    # Find all tags of the input track
    try:
        tags = soup.find('section', class_='catalogue-tags').find_all('li', class_='tag')
        for tag in tags:
            track_tag = tag.text
            track_tags.append(track_tag)
    except:
        pass
    
    # Find all similar tracks (12) of the input track
    try:
        tracks = soup.find_all('li', class_='column-tracks-item-wrap')
        for similar_track in tracks:
            address_info = similar_track.find('h3', class_='column-tracks-item-name')
            similar_track_name = address_info.find('a').text
            relative_track_url = address_info.find('a').get('href')
            similar_track_url = f'{BASE_URL}{relative_track_url}'
            similar_track_artist_name = similar_track.find('p', class_='column-tracks-item-artist').find('span').text.strip()
            similar_tracks.append(TrackInfoModel(similar_track_name, similar_track_url, similar_track_artist_name))
    except:
        pass
    
    track_info = TrackModel(TrackInfoModel(track_name, track_url, artist_name), track_length, album_name, track_tags, similar_tracks)
    return track_info



def start_track_info_request(track_url: str) -> TrackModel:
    response = requests.get(track_url)
    return parse_track_info(response.text, track_url)


def parse_listening_history(response: str) -> TrackListeningHistoryModel:
    listening_history = defaultdict(list)
    soup = BeautifulSoup(response, 'html.parser')
    tracklist_section = soup.find_all('section', class_='tracklist-section')
    for section in tracklist_section:
        _date = section.h2.text
        tracks = section.find_all('tr', class_='chartlist-row chartlist-row--with-artist chartlist-row--with-buylinks js-focus-controls-container')
        for track in tracks:
            # track_name = track.select_one('.chartlist-name').text.strip()
            # artist_name = track.select_one('.chartlist-artist').text.strip()
            relative_url = track.find('td', class_='chartlist-name').find('a').get('href')
            track_url = f'{BASE_URL}{relative_url}'
            listening_time = track.select_one('.chartlist-timestamp.chartlist-timestamp--lang-en').find('span').get('title')
            track_info = start_track_info_request(track_url)
#             track_model = TrackListeningHistoryModel(_date, listening_time, track_info)
#             listening_history[_date].append(track_model)
            return
    # ....


def start_request(url: str):
    response = requests.get(url)
    parse_listening_history(response.text)
    
def print_track_info(track_info: TrackInfoModel):
    print(f'Song: {track_info.track_name} \nSinger: {track_info.artist_name} \nURLs: {track_info.track_url}')

def print_similar_tracks(similar_tracks: List[TrackInfoModel]):
    print(f'There are {len(similar_tracks)} similar tracks.')
    for ind, track in enumerate(similar_tracks):
        print(ind)
        print_track_info(track)
    
if __name__ == '__main__':
    start_request(f'{START_URL}?page=1')


