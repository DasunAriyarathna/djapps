
import datetime, random, sha
import smtplib

from google.appengine.ext import db
from google.appengine.api import users
from simplejson.encoder import JSONEncoder as jenc
from simplejson.decoder import JSONDecoder as jdec

def get_channel_segments(channel):
    return channel.split("/")

