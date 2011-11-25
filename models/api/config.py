import os

# user related prefixes
MEMCACHE_USER_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".user."
MEMCACHE_TRACKS_USER_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".tracks.user"
MEMCACHE_SESSIONS_USER_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".sessions.user."