
"""
A django implementation of the OpenIDStore interface that uses the model
backend as its backing store.
Stores associations, nonces, and authentication tokens.

OpenIDStore is an interface from JanRain's OpenID python library:
  http://openidenabled.com/python-openid/

For more, see openid/store/interface.py in that library.
"""

import datetime

from openid.association import Association as OpenIDAssociation
from openid.store.interface import OpenIDStore
from openid.store import nonce
from models import Association, UsedNonce

# number of associations and nonces to clean up in a single request.
CLEANUP_BATCH_SIZE = 50

