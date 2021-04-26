import json
import os
from datetime import datetime, timedelta
from tempfile import gettempdir

class Cache():
  TIMESTAMP_FORMAT = "%Y-%m-%d-%H-%M"
  CACHE_FILE = "gcptree-cache.json"

  def __init__(self, ttl_hours=1, cache_file=CACHE_FILE):
    self.data = {}
    self.ttl_hours = ttl_hours
    self.cache_file = cache_file
    self.filename = os.path.join(gettempdir(), self.cache_file)
    if os.path.exists(self.filename):
      with open(self.filename, 'r') as f:
        data = json.load(f)
        self.data = self.updated_data(data)
        
  def updated_data(self, data):
    # A v1 cache (using CRM instead of CAI) is not compatible, so we simply overwrite it
    if '_v2' not in data:
      return {}
    if '_ttl' in data:
      self.ttl_hours = data['_ttl']
    previous_timestamp = datetime.strptime(data['_timestamp'], self.TIMESTAMP_FORMAT)
    if previous_timestamp > datetime.now() - timedelta(hours=self.ttl_hours) :
      return data
    return {}

  def is_empty(self):
    return len(self.data) == 0

  def has(self, key):
    return key in self.data

  def get(self, key):
    if self.has(key):
      return self.data[key]

  def add(self, key, value):
    self.data[key] = value
  
  def timestamp(self):
    return datetime.now().strftime(self.TIMESTAMP_FORMAT)
  
  def write(self):
    self.data['_timestamp'] = self.timestamp()
    self.data['_ttl'] = self.ttl_hours
    self.data['_v2'] = True
    with open(self.filename, 'w') as f:
      json.dump(self.data, f)

  def message(self):
    hours = 'an hour'
    if self.ttl_hours > 1:
      hours = "{} hours". format(self.ttl_hours)
    return 'INFO: Fetching GCP Resources, this may take a while (these results will be cached for {} in {})... '.format(hours, self.filename)

class NoCache():
  def is_empty(self):
    return True

  def has(self, key):
    return False

  def get(self, key):
    return None

  def add(self, key, value):
    return None

  def write(self):
    pass

  def message(self):
    return 'INFO: Cache will not be used.'