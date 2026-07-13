#                      ######################              ####
####               ##   ######################           ########
####             ####            ####                   ####  ####
####           ######            ####                  ####    ####
####          #######            ####                 ####      ####
####        #########            ####                ####        ####
####      #####  ####            ####               ####          ####
####    #####    ####            ####              ####            ####
####  #####      ####            ####             ####              ####
#########        ####            ####            ####                ####            +----  +----\   |  /
#######          ####            ####       ##################################       |      |     |  | /
#####            ####            ####      ####################################  -   +---+  |     |  ++
###              ####            ####      ####                            ####          |  |     |  | \
#                ####            ###       ####                            ####      ----+  +----/   |  \
"""
iii     iii tttttttttt   ddddddddd       |
iii   iiiii     ttt      ddd   ddd
iii iii iii     ttt      ddd   ddd
iiiii   iii     ttt    ddddddddddddddd
iiii    iii     ttt    dd           dd

    ssssssss  dddddddd    kkk   kkk
   sss        ddd   ddd   kkk   kkk
   sss        ddd    ddd  kkk   kkk
     sssssss  ddd    ddd  kkk  kkk
         sss  ddd    ddd  kkkkkk
         sss  ddd   ddd   kkk  kkk
    ssssss    dddddddd    kkk   kkk

                          by fi.res
                    @fdg | @itd_sdk
"""

from importlib.metadata import version
from time import sleep

__version__ = version('itd-sdk')

from itd._default import LimiterConfig, limiters
from itd._default import set_config as set_limiter_config
from itd._limiter import BurstRateLimiter, HalfRateLimiter, IPRateLimiter, RateLimiter
from itd.clan import Clan, TopClans
from itd.client import Client as ITDClient
from itd.client import Config as ITDConfig
from itd.client import init_client
from itd.file import File
from itd.hashtag import Hashtag, Hashtags
from itd.notification import Notifications
from itd.poll import NewPoll
from itd.post import HashtagPosts, LikedPosts, Post, Posts, UserPosts
from itd.session import Sessions
from itd.user import Me, User, Users, get_follow_status
from itd.version import Apps, Changelog


# call if you set auto_acquire=False in the end of cycle
def acquire_limiters():
    sleep(max((limiter.delay for limiter in limiters.values() if limiter.used), default=0))

    for limiter in limiters.values():
        limiter.used = False


__all__ = [
    '__version__',
    'Changelog',
    'Apps',
    'ITDClient',
    'ITDConfig',
    'init_client',
    'Clan',
    'TopClans',
    'File',
    'Hashtag',
    'Hashtags',
    'Notifications',
    'Post',
    'Posts',
    'UserPosts',
    'HashtagPosts',
    'LikedPosts',
    'NewPoll',
    'Sessions',
    'User',
    'Me',
    'Users',
    'get_follow_status',
    'set_limiter_config',
    'LimiterConfig',
    'BurstRateLimiter',
    'RateLimiter',
    'HalfRateLimiter',
    'IPRateLimiter',
    'acquire_limiters'
]
