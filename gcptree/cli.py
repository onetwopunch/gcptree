import argparse
import json
import sys
from googleapiclient.errors import HttpError
from colorama import init, Fore, Style
from .tree import Tree
from .cache import Cache, NoCache

VERSION = "0.2.0"

class Cli:
  LEAF      = "└── "
  LEAF_PLUS = "├── "
  BAR_SPACE = "│   "
  SPACE     = "    "

  def __init__(self):
    init()

    parser = argparse.ArgumentParser(description='Print out a GCP org heirarchy', prog="gcptree", epilog="Version: {}".format(VERSION))
    parser.add_argument('org_id', nargs=1, 
                        help='GCP Organization ID')
    parser.add_argument('--format', default="text",
                        help='Output format (json or text)')
    parser.add_argument('--full-resource', action='store_const',
                        const=True, default = False,
                        help='API-parsable nodes where org and folder resource names are not resolved, i.e org/123 instead of example.com')
    parser.add_argument('--no-cache', action='store_const',
                        const=True, default = False,
                        help='If set, cache will not be used.')
    parser.add_argument('--cache-ttl', default=1, type=int,
                        help='Number of hours to keep the cache, default is 1.')

    self.args = parser.parse_args()
  
  def build_tree(self):
    cache = Cache(ttl_hours=self.args.cache_ttl)
    if self.args.no_cache:
      cache = NoCache()
    if cache.is_empty():
      print(cache.message(), file=sys.stderr)
    t = Tree(self.args.org_id[0], full_resource=self.args.full_resource, cache_inst=cache)
    try:
      return t.build()
    except HttpError as e:
      if e.resp.status == 403:
        print(self.permission_help())
        sys.exit(1)
  
  def is_project(self, obj):
    return len(obj) > 0 and 'projectId' in obj

  def walk(self, tree, prefix=""):
    nodes = sorted(tree.keys())
    for i, node in enumerate(nodes):
      lchar, schar = (self.LEAF, self.SPACE) if i == len(nodes) - 1 else (self.LEAF_PLUS, self.BAR_SPACE)
      if self.is_project(tree[node]):
        formatted = node
        if tree[node]['state'] != 'ACTIVE':
          formatted = Style.DIM + node + Style.RESET_ALL
        print(prefix + lchar + formatted)
      else:
        print(prefix + lchar + Style.BRIGHT + Fore.BLUE + node + Style.RESET_ALL)
        self.walk(tree[node], prefix + schar)

  def print_tree(self, tree):
    org = list(tree.keys())[0]
    print(Fore.GREEN + Style.BRIGHT + org + Style.RESET_ALL)
    self.walk(tree[org])

  def run(self):
    tree = self.build_tree()
    if self.args.format == 'json':
      print(json.dumps(tree, sort_keys=True, indent=4))
    elif self.args.format == 'text':
      self.print_tree(tree)
    else:
      print("Unsupported format")

  def permission_help(self):
    msg = """
GCP Permission Error. Make sure you have the following roles at the org level:
- roles/browser
- roles/cloudasset.viewer

If you're using a service account, ensure that the correct key file path is
referenced in the environment variable: GOOGLE_APPLICATION_CREDENTIALS
"""
    return Style.BRIGHT + Fore.RED + msg + Style.RESET_ALL