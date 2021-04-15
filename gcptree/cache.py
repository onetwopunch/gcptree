import json
import os
from datetime import datetime, timedelta
from tempfile import gettempdir

TIMESTAMP_FORMAT = "%Y-%m-%d-%H-%M"
class Cache():
  def __init__(self):
    self.filename = os.path.join(gettempdir(), "gcptree-cache.json")
    self.data = {}
    if os.path.exists(self.filename):
      with open(self.filename, 'r') as f:
        data = json.load(f)
        previous_timestamp = datetime.strptime(data['_timestamp'], TIMESTAMP_FORMAT)
        if datetime.now()  > previous_timestamp - timedelta(hours=1):
          self.data = data
  
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
    return datetime.now().strftime(TIMESTAMP_FORMAT)
  
  def write(self):
    self.data['_timestamp'] = self.timestamp()
    with open(self.filename, 'w') as f:
      json.dump(self.data, f)
