from typing import List

class TrackInfoModel:

    def __init__(self, track_name: str, track_url: str, artist_name: str):
        self.track_name = track_name 
        self.track_url = track_url # PRIMARY KEY
        self.artist_name = artist_name
        
    def get_info(self):
        return [self.track_name, self.track_url, self.artist_name]


class TrackModel:

    def __init__(self, track_info: TrackInfoModel, track_length: str, album_name: str, tags: List[str], similar_track_urls: List[str]):
        self.track_info = track_info
        self.track_length = track_length
        self.album_name = album_name
        self.tags = tags
        self.similar_track_urls = similar_track_urls
        
    def get_info(self) -> List[str]:
        info = self.track_info.get_info()
#         info.extend(self.track_length, self.album_name, self.tags, self.similar_track_urls)
#         return info

        return[*info, self.track_length, self.album_name, self.tags, self.similar_track_urls]

#     def get_similar_track(self) -> List[str]:
        

        
class TrackListeningHistoryModel:

    def __init__(self, _date: str, _time: str, track: TrackModel):
        self.date = _date
        self.time = _time
        self.track = track
        
    def get_info(self) -> List[str]:
        info = self.track.get_info()
        return [self.date, self.time, *info]
    

class ListeningHistoryModel:
    
    def __init__(self, _date, tracks: List[TrackListeningHistoryModel]):
        self.date = _date
        self.tracks = tracks


