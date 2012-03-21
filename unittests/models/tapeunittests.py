"""
	Unit testing for the tapes model.
"""

import unittest
from google.appengine.ext import testbed

from models.db.track import Track
from models.db.station import Station
from models.db.tape import Tape
from models.db.tape import CompilationTrack

class TapeUnitTest(unittest.TestCase):
	"""
		Testing the Tape model.
	"""

	def setUp(self):
		# First, create an instance of the Testbed class.
	    self.testbed = testbed.Testbed()
	    # Then activate the testbed, which prepares the service stubs for use.
	    self.testbed.activate()
	    # Next, declare which service stubs you want to use.
	    self.testbed.init_datastore_v3_stub()

	def tearDown(self):
		self.testbed.desactivate()
	
	def testAddingTrackToCompilation(self):
		#Creating Station
		station = Station(
			shortname = "testStation",
			link = "https://www.facebook.com/pages/Fans-of-Old-School-Hip-Hop/129247123864094", 
			name ="Test Station")
		station.put()

		#Creating 2 tracks
		track_1 = Track(youtube_id ="iOKFiGyAmMQ", station = station )
		track_1.put()

		track_2 = Track(youtube_id ="Zdrga0MwoS8", station = station )
		track_2.put()

		#Creating a tape
		tape = Tape(tape_name = "Test Tape")
		tape.put()

		#Adding tracks to tape
		tape.tracks.append(track_1.key())
		tape.tracks.append(track_2.key())

if __name__ == '__main__':
    unittest.main()







