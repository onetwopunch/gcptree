from googleapiclient import discovery
from deepmerge import merge_or_raise
import sys
import json

class Tree():
  # Disable all the no-member violations in this class
  # pylint: disable=no-member
  def __init__(self, org_id, resolve=False):
    self.org = f"organizations/{org_id}"
    self.resolve = resolve

  def build(self):
    self.crm = discovery.build('cloudresourcemanager', 'v1')
    request = self.crm.projects().list()
    tree = {}
    while request:
      response = request.execute()
      for project in response.get('projects', []):
        ancestry = self.get_ancestry_names(project["projectId"])
        print(ancestry)
        if self.resolve:
          ancestry = self.resolve_ancestry(ancestry)
        tree = self.graft(tree, ancestry, project)
      request = self.crm.projects().list_next(previous_request=request, previous_response=response)
    return tree
  
  def graft(self, tree, ancestry, metadata):
    branch = self.ancestry_branch(ancestry, metadata)
    return merge_or_raise.merge(tree, branch)
  
  def ancestry_branch(self, ancestry, metadata):
    res = {ancestry.pop(): metadata}
    while len(ancestry) > 0:
      res = {ancestry.pop(): res}
    return res
  
  def resolve_ancestry(self, ancestry):
    # TODO: Implement
    return ancestry  
  
  def get_ancestry_names(self, project_id):
    response = self.crm.projects().getAncestry(projectId=project_id).execute()
    return list(reversed([f"{i['resourceId']['type']}s/{i['resourceId']['id']}" for i in response["ancestor"]]))