"""
	Unit testing for the tapes model.
"""

import unittest
from google.appengine.ext import testbed

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
		