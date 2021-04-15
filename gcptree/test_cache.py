import pytest
from datetime import datetime, timedelta
from .cache import Cache

def test_cache_loaded():
  inst = Cache()
  a_few_minutes_ago = datetime.now() - timedelta(minutes=15)
  data = {"_timestamp": a_few_minutes_ago.strftime(inst.TIMESTAMP_FORMAT), "key":"value"}
  assert len(inst.updated_data(data)) > 0

def test_cache_busted():
  inst = Cache()
  over_an_hour_ago = datetime.now() - timedelta(minutes=90)
  data = {"_timestamp": over_an_hour_ago.strftime(inst.TIMESTAMP_FORMAT), "key":"value"}
  assert len(inst.updated_data(data)) == 0