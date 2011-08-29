import logging, re

from datetime import datetime
from datetime import timedelta

from database.track import Track
from google.appengine.ext import db

class Queue():
	
	@staticmethod
	def putSomeDefaultData():
		query = Track.all()
		query.order("-expiration_time")
		query.filter("expiration_time >", datetime.now())
		aTrack = query.get()
		
		if not(aTrack):
			logging.info("We have to put some data to do the tests")
			videos = [{
				"title" : "Breakbot - Baby I'm Yours (feat. Irfane) - HD",
				"id" : "6okxuiiHx2w",
				"thumbnail" : "http://i.ytimg.com/vi/6okxuiiHx2w/default.jpg",
				"duration" : 151,
			},{
				"title" : "Breakbot - Fantasy feat. Ruckazoid",
				"id" : "ShiKVmNnp9w",
				"thumbnail" : "http://i.ytimg.com/vi/ShiKVmNnp9w/default.jpg",
				"duration" : 194,
			}]
			
			i = 1
			durationSongsBeforeInSeconds = 0
			for video in videos:
				track = Track(
					youtube_title = video["title"],
					youtube_id = video["id"],
					youtube_thumbnail_url = video["thumbnail"],
					youtube_duration = video["duration"],
				)
				
				durationSongsBeforeInSeconds += video["duration"]
					
				durationSongsBefore = timedelta(0, durationSongsBeforeInSeconds)
				track.expiration_time = datetime.now() + durationSongsBefore
				
				track.put()
				
				i = i+1	
		else:
			logging.info("We don't need to add some data")
	
	# This method is called when a client initially requests the songs that are not expired (live or in the queue)
	@staticmethod
	def getNonExpiredTracks():
		datetimeNow = datetime.now()
		
		query = Track.all()
		query.filter("expiration_time >", datetimeNow)
		query.order("expiration_time")
		
		nonExpiredTracks = query.fetch(10)
		
		return nonExpiredTracks
	
	#This method is called via AJAX requests every 30 seconds
	@staticmethod
	def getNewNonExpiredTracks(additionTime):
		
		addition_time = Queue.parseDateTime(additionTime)
		
		query = Track.all()
		query.filter("addition_time >", addition_time)
		query.order("addition_time")
		
		newNonExpiredTracks = query.fetch(10)
		
		return newNonExpiredTracks		
	
	#This method is used to transform a string to a datetime object
	@staticmethod
	def parseDateTime(string):	
		m = re.match(r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2}) (?P<hours>\d{2}):(?P<minutes>\d{2}):(?P<seconds>\d{2}).(?P<microseconds>\d{6})", string)
		year = m.group("year")
		month = m.group("month")
		day = m.group("day")
		hours = m.group("hours")
		minutes = m.group("minutes")
		seconds = m.group("seconds")
		microseconds = m.group("microseconds")
		
		dateTimeToBeReturned = datetime(int(year), int(month), int(day), int(hours), int(minutes), int(seconds), int(microseconds))
		
		return dateTimeToBeReturned
		
	
	# This method adds a new track to the list
	@staticmethod
	def addToQueue(title, id, thumbnail, duration):
		datetimeNow = datetime.now()
		
		query = Track.all()
		query.filter("expiration_time >", datetimeNow)
		query.order("-expiration_time")
		
		lastTrackInTheQueue = query.get()
		
		newTrackExpirationTime = timedelta(0,int(duration))
		if(lastTrackInTheQueue):
			newTrackExpirationTime += lastTrackInTheQueue.expiration_time
		else:
			newTrackExpirationTime += datetimeNow
		
		newTrack = Track(
			youtube_title = title,
			youtube_id = id,
			youtube_thumbnail_url = db.Link(thumbnail),
			youtube_duration = int(duration),
			expiration_time = newTrackExpirationTime,
		)
		
		newTrack.put()
		logging.info("New track in the list: %s" % title)
		
		