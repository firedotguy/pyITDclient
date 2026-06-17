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

__version__ = version("itd-sdk")

from itd._default import limiters
from itd.clan import Clan, TopClans
from itd.client import Client as ITDClient
from itd.client import Config as ITDConfig
from itd.file import File
from itd.hashtag import Hashtag, Hashtags
from itd.notification import Notifications
from itd.poll import NewPoll
from itd.post import HashtagPosts, LikedPosts, Post, Posts, UserPosts
from itd.session import Sessions
from itd.user import Me, User, Users, get_follow_status
from itd.version import Apps, Changelog


def acquire_limiters():
    for limiter in limiters.values():
        limiter.acquire()


__all__ = [
    'Changelog',
    'Apps',
    'ITDClient',
    'ITDConfig',
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
    'acquire_limiters'
]
