import json
import os
from datetime import datetime, timedelta
from tempfile import gettempdir

class Cache():
  TIMESTAMP_FORMAT = "%Y-%m-%d-%H-%M"

  def __init__(self):
    self.data = {}
    self.filename = os.path.join(gettempdir(), "gcptree-cache.json")
    if os.path.exists(self.filename):
      with open(self.filename, 'r') as f:
        data = json.load(f)
        self.data = self.updated_data(data)
        
  def updated_data(self, data):
    previous_timestamp = datetime.strptime(data['_timestamp'], self.TIMESTAMP_FORMAT)
    if previous_timestamp > datetime.now() - timedelta(hours=1) :
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
    with open(self.filename, 'w') as f:
      json.dump(self.data, f)
