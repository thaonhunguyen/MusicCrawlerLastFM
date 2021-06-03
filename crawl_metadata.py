from __future__ import with_statement
from models import *
from bs4 import BeautifulSoup
from collections import defaultdict

import os
import os.path as osp
import requests
import json
from tqdm import tqdm
from datetime import *
import csv
import argparse


# Define some constants here
BASE_URL = 'https://www.last.fm'
START_URL = 'https://www.last.fm/user/cgurrin/library' # base url
MASTER_PATH = '/home/ntnhu/DCU/PROJECTS/music_information_retrieval/'

parser = argparse.ArgumentParser(description='Crawl music data information from lastfm website')
parser.add_argument('--filename', '-f', type=str, required=True, help='File name to store the result of crawling')


def parse_track_info(response: str, track_url: str = None, find_similar: bool = True) -> TrackModel:
    '''
    Crawl information of 1 track from lastfm
    
    Parameters
    ----------
    - response: str
        
    - track_url: str
        URL of current track
    - find_similar: bool
        Whether to get information of similar track or not

        
    Returns
    -------
    - id (first word in the syn string)
    - name of the obj (which be used later
    '''
    # Initial beautifulsoup object, read form response
    soup = BeautifulSoup(response, 'html.parser')
    similar_track_urls, track_tags = [], []
    
    try:
        track_name = soup.find('h1', class_='header-new-title').text
    except:
        track_name = ''
    try:
        artist_name = soup.find('a', class_='header-new-crumb').find('span').text
    except:
        artist_name = ''
    try:
        track_length = soup.find('dd', class_='catalogue-metadata-description').text.strip()
    except:
        track_length = '0'
    try:
        album_name = soup.find('h4', class_='source-album-name').find('a').text
    except:
        album_name = ''
        
    # Find all tags of the input track
    try:
        tags = soup.find('section', class_='catalogue-tags').find_all('li', class_='tag')
        for tag in tags:
            track_tag = tag.text
            track_tags.append(track_tag)
    except:
        pass
    
    # Find all similar tracks (12) of the input track
    if find_similar:
        try:
            tracks = soup.find_all('li', class_='column-tracks-item-wrap')
            for similar_track in tracks:
                address_info = similar_track.find('h3', class_='column-tracks-item-name')
    #             similar_track_name = address_info.find('a').text
                relative_track_url = address_info.find('a').get('href')
                similar_track_url = f'{BASE_URL}{relative_track_url}'
    #             similar_track_artist_name = similar_track.find('p', class_='column-tracks-item-artist').find('span').text.strip()
                similar_track_urls.append(similar_track_url)
        except:
            pass
    
    track_info = TrackModel(TrackInfoModel(track_name, track_url, artist_name), track_length, album_name, track_tags, similar_track_urls)
#     track_info = TrackInfoModel(track_name, track_url, artist_name)
    return track_info



def start_track_info_request(track_url: str, find_similar = True) -> TrackModel:
    response = requests.get(track_url)
    return parse_track_info(response.text, track_url, find_similar = find_similar)


def parse_listening_history(response: str) -> TrackListeningHistoryModel:
    listening_history = defaultdict(list)
    soup = BeautifulSoup(response, 'html.parser')
    tracklist_section = soup.find_all('section', class_='tracklist-section')
    for section in tqdm(tracklist_section, desc='inner-loop', position=1, leave=False):
        _date = section.h2.text
        tracks = section.find_all('tr', class_='chartlist-row chartlist-row--with-artist chartlist-row--with-buylinks js-focus-controls-container')
        for track in tracks:
            relative_url = track.find('td', class_='chartlist-name').find('a').get('href')
            track_url = f'{BASE_URL}{relative_url}'
            listening_timestamp = track.select_one('.chartlist-timestamp.chartlist-timestamp--lang-en').find('span').get('title')
            listening_date, listening_time = convert_date_time(listening_timestamp)
            track_info = start_track_info_request(track_url)
            track_model = TrackListeningHistoryModel(listening_date, listening_time, track_info)
            listening_history[_date].append(track_model)
#             listening_history[_date].append(track_info)
#             return
    # ....
    return listening_history

def start_request(url: str, find_similar=True):
    response = requests.get(url)
#     parse_listening_history(response.text)
    return parse_listening_history(response.text)


def get_max_page_number(url: str) -> int:
    # get max page number from start url 
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    page_numbers = soup.find_all('li', class_='pagination-page')
    page_number = page_numbers[-1].find('a').text
    return int(page_number)

def convert_date_time(timestamp: str, time_format="%A %d %b %Y, %I:%M%p") -> List[str]:
    timestamp = datetime.strptime(timestamp, time_format)
    date_ = timestamp.strftime("%Y-%m-%d")
    time_ = timestamp.strftime("%H:%M")
    return [date_, time_]
    
def display_track_info(track_info_model: TrackInfoModel):
    # display information of 1 track
    print(f'Song: {track_info_model.track_name} \nSinger: {track_info_model.artist_name} \nURLs: {track_info_model.track_url}')
    
def get_similar_tracks(url_list: List[str]) -> List[TrackModel]:
    # get similar tracks from list of similar track urls
    return[start_track_info_request(url, find_similar=False) for url in url_list]

# def print_similar_tracks(similar_tracks: List[TrackInfoModel]):
#     print(f'There are {len(similar_tracks)} similar tracks.')
#     for ind, track in enumerate(similar_tracks):
#         print(ind)
#         print_track_info(track)  
    
def save_track_info(track_info_list: defaultdict, filename: str, header: List[str]):
    # save a list of track model to csv file with corresponding date
    # header is the header of csv file (assign to variable of TrackModel)
    try:
        with open(filename, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for day, info in tqdm(track_info_list.items()):
                for item in info:
                    track_info = item.get_info()
                    writer.writerow([day, *track_info])
    except BaseException as e:
        print('BaseException:', filename)
    else:
        print(f'Data has been saved to {filename} successfully !')
    
def to_dict(obj):
    # convert a class object to dictionary
    return json.loads(json.dumps(obj, default=lambda o: o.__dict__))

def save_json(obj, file_name):
    # save object to json-format file
    try:
        with open(file_name, 'w') as file:
            json.dump(obj, file)
        print(f'Successfully write objects to {file_name} file.')
        
    except EnvironmentError: # parent of IOError, OSError *and* WindowsError where available
        print('oops')
    
    
def load_json(file_name):
    # load json-format file
    try:
        print(f'Loading objects from {file_name} file.')
        with open(file_name, 'r') as file:
            data = json.load(file)
        return data
        
    except EnvironmentError: # parent of IOError, OSError *and* WindowsError where available
        print('oops')

# def main(args):
    
    
    
if __name__ == '__main__':
#     result = start_request(f'{START_URL}?page=1')
#     save_json(result, 'result_page1.json')
    MAX_PAGE_NUMBER = get_max_page_number(START_URL) # adjust max page number to fit the maximum crawling page of each person
    start_urls = [f'{START_URL}?page={page_no}' for page_no in range(1, MAX_PAGE_NUMBER+1)]
    header = ['date', 'listening_date', 'listening_time', 'track_name', 'track_url', 'artist_name', 'track_length', 'track_album', 'track_tags', 'similar_track_urls']
    
#     args = parser.parse_args()
    filename = os.path.join(MASTER_PATH, 'dataset', 'lastfm_music_data.csv')
    
    result = defaultdict(list)
    for url_page in tqdm(start_urls[:600], desc='outer-loop', position=0):
        track_list = defaultdict(list)
    #     url_page = f'{START_URL}?page={i}'
        track_list = start_request(url_page)
        for key, value in track_list.items():
            result[key].extend(value)
            
    save_track_info(result, filename = filename, header=header)
    print('Done')

