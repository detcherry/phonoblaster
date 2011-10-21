import os

# Station related prefixes
MEMCACHE_STATION_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".station."
MEMCACHE_STATION_CONTRIBUTORS_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".contributors.station."
MEMCACHE_STATION_TRACKLIST_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".tracklist.station."
MEMCACHE_STATION_SESSIONS_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".sessions.station."

# User related prefixes
MEMCACHE_USER_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".user."
MEMCACHE_USER_FACEBOOK_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".user.facebook."