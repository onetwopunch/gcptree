import argparse
import json
from .tree import Tree

class Cli:
  def __init__(self):
    parser = argparse.ArgumentParser(description='Print out a GCP org heirarchy', prog="gcptree")
    parser.add_argument('org_id', nargs=1, 
                        help='GCP Organization ID')
    parser.add_argument('--format', default="json",
                        help='Output format (json or text)')
    parser.add_argument('--no-resolve', action='store_const',
                        const=sum, default=False,
                        help='API-parsable nodes where org and folder ids are not resolved')

    self.args = parser.parse_args()
  
  def build_tree(self):
    return Tree(self.args.org_id, not self.args.no_resolve).build()
  
  def run(self):
    t = self.build_tree()
    if self.args.format == 'json':
      print(json.dumps(t, sort_keys=True, indent=4))
    else:
      print("Unsupported format")