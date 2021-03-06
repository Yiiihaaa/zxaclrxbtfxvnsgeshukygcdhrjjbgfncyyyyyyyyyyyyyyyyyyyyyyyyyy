"""
Hifumi
~~~~~~~~~~~~~~~~~~~

Hifumi, a multifunctional Discord bot.

:copyright: (c) 2017 Hifumi - the Discord Bot Project
:license: Apache License 2.0, see LICENSE for more details.

"""
from collections import namedtuple

from bot.hifumi import Hifumi
from bot.session_manager import HTTPStatusError, SessionManager

VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')

version_info = VersionInfo(
    major=0, minor=2, micro=0, releaselevel='alpha', serial=1
)

__title__ = 'Hifumi'
__author__ = ['Underforest#1284', 'InternalLight#9391', 'ラブアローシュート#6728']
__author_plain__ = ['Underforest', 'InternalLight', 'MaT1g3R']
__helper__ = ['Wolke#6746']
__helper_plain__ = ['DasWolke']
__license__ = 'Apache License 2.0'
__copyright__ = 'Copyright 2017 Hifumi - the Discord Bot Project'
__version__ = '.'.join([str(i) for i in list(version_info)[:3]])

__all__ = ['__title__', '__author__', '__author_plain__',
           '__helper__', '__helper_plain__', '__license__', '__copyright__',
           '__version__', 'version_info', 'Hifumi', 'SessionManager',
           'HTTPStatusError']
