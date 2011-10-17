import os

MEMCACHE_STATION_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".station."
MEMCACHE_STATION_CONTRIBUTORS_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".contributors.station."
MEMCACHE_STATION_TRACKLIST_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".tracklist.station."
MEMCACHE_STATION_SESSIONS_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".sessions.station."