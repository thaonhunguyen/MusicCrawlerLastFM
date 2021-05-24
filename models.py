from typing import List

class TrackInfoModel:

    def __init__(self, track_name: str, track_url: str, artist_name: str):
        self.track_name = track_name 
        self.track_url = track_url # PRIMARY KEY
        self.artist_name = artist_name


class TrackModel:

    def __init__(self, track_info: TrackInfoModel, track_length: str, album_name: str, tags: List[str], similar_tracks: List[TrackInfoModel]):
        self.track_info = track_info
        self.track_length = track_length
        self.album_name = album_name
        self.tags = tags
        self.similar_tracks = similar_tracks

        
class TrackListeningHistoryModel:

    def __init__(self, _date: str, _time: List[str], track: TrackModel):
        self.date = _date
        self.time = _time
        self.track = track
    

class ListeningHistoryModel:
    
    def __init__(self, _date, tracks: List[TrackListeningHistoryModel]):
        self.date = _date
        self.tracks = tracks


