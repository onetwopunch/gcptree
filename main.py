from googleapiclient import discovery
from deepmerge import merge_or_raise
import sys
import json
  
class GTree():
  def __init__(self, org_id):
    self.crm = discovery.build('cloudresourcemanager', 'v1')
    self.org = f"organizations/{org_id}"
   # TODO: replace ids with human-readable names
  def build(self):
    request = self.crm.projects().list()
    tree = {}
    while request:
      response = request.execute()
      for project in response.get('projects', []):
        ancestry = self.getAncestryNames(project["projectId"])
        branch = self.ancestryTree(project, ancestry)
        tree = merge_or_raise.merge(tree, branch)
      request = self.crm.projects().list_next(previous_request=request, previous_response=response)
    return tree
  
  def ancestryTree(self, project, ancestry):
      res = {ancestry.pop(): project}
      while len(ancestry) > 0:
        res = {ancestry.pop(): res}
      return res
      
  def getAncestryNames(self, project_id):
    response = self.crm.projects().getAncestry(projectId=project_id).execute()
    return list(reversed([f"{i['resourceId']['type']}s/{i['resourceId']['id']}" for i in response["ancestor"]]))

if __name__ == "__main__":
  tree = GTree(sys.argv[1]).build()
  print(json.dumps(tree))