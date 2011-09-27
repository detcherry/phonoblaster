import logging

from datetime import datetime
from datetime import timedelta
from random import randrange

from db.track import Track
from db.station import Station
from db.session import Session

from notifiers.track import TrackNotifier

from google.appengine.ext import db

class Queue():
	
	def __init__(self, station_key):
		self.station = Station.get(station_key)
	
	def getTracks(self):
		query = Track.all()
		query.filter("station", self.station.key())
		query.filter("expired >", datetime.now())
		query.order("expired")
		
		tracks = query.fetch(10)
		
		return tracks
	
	@property
	def numberOfTracks(self):
		query = Track.all()
		query.filter("station", self.station.key())
		query.filter("expired >", datetime.now())
		query.order("expired")
		number = query.count()		
		return number
	
	def addTrack(self, title, id, thumbnail, duration, user_key):
		tracks = self.getTracks()
		if(len(tracks) == 10):
			return None
		else:
			expiration_interval = timedelta(0,int(duration))
			
			if(len(tracks) == 0):
				expiration_time = datetime.now() + expiration_interval
			else:
				last_track = tracks[-1]
				expiration_time = last_track.expired + expiration_interval

			newTrack = Track(
				youtube_title = title,
				youtube_id = id,
				youtube_thumbnail_url = db.Link(thumbnail),
				youtube_duration = int(duration),
				station = self.station.key(),
				submitter = user_key,
				expired = expiration_time,
			)
			newTrack.put()
	
			logging.info("New track %s in the %s tracklist" %(title, self.station.identifier))
			
			return newTrack

	def shuffle(self, user_key):
		latest_tracks = Track.all().filter("submitter", user_key).order("-added").fetch(50)
		number_of_latest_tracks = len(latest_tracks)
		non_expired_tracks = self.getTracks()		
		number_of_remaining_tracks = 10 - len(non_expired_tracks)
		random_tracks = []
				
		for i in range(0, number_of_remaining_tracks):
			random_integer = randrange(number_of_latest_tracks)
			random_track = latest_tracks[random_integer]
			track_added = self.addTrack(random_track.youtube_title, random_track.youtube_id, random_track.youtube_thumbnail_url, random_track.youtube_duration, user_key)
			random_tracks.append(track_added)
		
		return random_tracks
	
	def deleteTrack(self, track_key):
		track_to_delete = Track.get(track_key)
		if(track_to_delete):
			tracks_to_edit = Track.all().filter("expired >", track_to_delete.expired)
	
			offset = timedelta(0, track_to_delete.duration)
			for track in tracks_to_edit:
				track.expired -= offset
				track.put()
	
			soon_deleted_track_name = track_to_delete.youtube_title
	
			track_to_delete.delete()
			logging.info("Track %s removed from database" %(soon_deleted_track_name))
	
			return True
		else:
			return False
			
			
			
		