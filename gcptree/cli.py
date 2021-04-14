import argparse
import json
from .tree import Tree

LEAF = "└──"
LEAF_PLUS = "├──"
SPACE = "│  "

class Cli:
  def __init__(self):
    parser = argparse.ArgumentParser(description='Print out a GCP org heirarchy', prog="gcptree")
    parser.add_argument('org_id', nargs=1, 
                        help='GCP Organization ID')
    parser.add_argument('--format', default="text",
                        help='Output format (json or text)')
    parser.add_argument('--faster', action='store_const',
                        const=True, default = False,
                        help='API-parsable nodes where org and folder ids are not resolved')

    self.args = parser.parse_args()
  
  def build_tree(self, include_project_metadata):
    return Tree(self.args.org_id, self.args.faster).build(include_project_metadata)
  
  def format_node(self, node, level=0, is_last=False):
    f = ""
    f += SPACE * (level - 1)
    if level > 0:
      f += LEAF if is_last else LEAF_PLUS
      f += " "
    f += f"{node}\n" 
    return f
  
  def formatted_tree(self, tree):
    formatted = ""
    level = 0
    # Queue contains the key, entire subtree, it's level,and whether it's last
    # e.g. ("example.com", {...}, 0, False) is an org node that is at the
    # top level and it's not the last node in a list.
    org = list(tree.keys())[0]
    queue = [(org, tree[org], 0, False)]
    while queue:
      key, subtree, level, is_last = queue.pop()
      formatted += self.format_node(key, level, is_last)
      if subtree:
        # Since we're using a queue the one that appears
        # last is enqueued first
        last_key = list(subtree.keys())[0]
        for k, v in subtree.items():
          queue.append((k, v, level + 1, k == last_key))
    return formatted
  
  def run(self):
    if self.args.format == 'json':
      tree = self.build_tree(True)
      print(json.dumps(tree, sort_keys=True, indent=4))
    elif self.args.format == 'text':
      tree = self.build_tree(False)
      print(self.formatted_tree(tree))
    else:
      print("Unsupported format")

if __name__ == "__main__":
  import json, sys
  with open(sys.argv[1]) as f:
    data = json.load(f)
    print(Cli().formatted_tree(data))