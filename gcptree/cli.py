import argparse
import json
import sys
from colorama import init, Fore, Style
from .tree import Tree
from .cache import Cache

LEAF      = "└── "
LEAF_PLUS = "├── "
BAR_SPACE = "│   "
SPACE     = "    "

class Cli:
  def __init__(self):
    init()
    parser = argparse.ArgumentParser(description='Print out a GCP org heirarchy', prog="gcptree")
    parser.add_argument('org_id', nargs=1, 
                        help='GCP Organization ID')
    parser.add_argument('--format', default="text",
                        help='Output format (json or text)')
    parser.add_argument('--full-resource', action='store_const',
                        const=True, default = False,
                        help='API-parsable nodes where org and folder resource names are not resolved, i.e org/123 instead of example.com')
    parser.add_argument('--cache-ttl', default=1, type=int,
                        help='Number of hours to keep the cache, default is 1.')

    self.args = parser.parse_args()
  
  def build_tree(self):
    cache = Cache(ttl_hours=self.args.cache_ttl)
    if cache.is_empty():
      print(cache.message(), file=sys.stderr)
    t = Tree(self.args.org_id[0], full_resource=self.args.full_resource, cache_inst=cache)
    return t.build()
  
  def is_project(self, obj):
    return len(obj) > 0 and 'projectId' in obj

  def walk(self, tree, prefix=""):
    nodes = sorted(tree.keys())
    for i, node in enumerate(nodes):
      lchar, schar = (LEAF, SPACE) if i == len(nodes) - 1 else (LEAF_PLUS, BAR_SPACE)
      if self.is_project(tree[node]):
        formatted = node
        if tree[node]['lifecycleState'] != 'ACTIVE':
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