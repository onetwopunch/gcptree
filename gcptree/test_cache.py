import pytest
from datetime import datetime, timedelta
from .cache import Cache

def test_cache_loaded():
  inst = Cache(cache_file="test.json")
  a_few_minutes_ago = datetime.now() - timedelta(minutes=15)
  data = {"_timestamp": a_few_minutes_ago.strftime(inst.TIMESTAMP_FORMAT), "_v2": True}
  assert len(inst.updated_data(data)) > 0

def test_cache_busted():
  inst = Cache(cache_file="test.json")
  over_an_hour_ago = datetime.now() - timedelta(minutes=90)
  data = {"_timestamp": over_an_hour_ago.strftime(inst.TIMESTAMP_FORMAT), "_v2": True}
  assert len(inst.updated_data(data)) == 0

def test_cache_loaded_2():
  inst = Cache(cache_file="test.json")
  a_few_minutes_ago = datetime.now() - timedelta(minutes=90)
  data = {"_timestamp": a_few_minutes_ago.strftime(inst.TIMESTAMP_FORMAT), "_ttl":2, "_v2": True}
  assert len(inst.updated_data(data)) > 0

def test_cache_busted_2():
  inst = Cache(cache_file="test.json")
  over_an_hour_ago = datetime.now() - timedelta(minutes=150)
  data = {"_timestamp": over_an_hour_ago.strftime(inst.TIMESTAMP_FORMAT), "_ttl":2, "_v2": True}
  assert len(inst.updated_data(data)) == 0