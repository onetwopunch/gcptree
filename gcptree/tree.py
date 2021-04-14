from googleapiclient import discovery
from deepmerge import merge_or_raise
import sys
import json

class Tree():
  # Disable all the no-member violations in this class
  # pylint: disable=no-member
  def __init__(self, org_id, resolve=True):
    self.org = f"organizations/{org_id}"
    self.resolve = resolve

  def build(self):
    # v1 is the only version that supports project ancestry
    self.crm_v1 = discovery.build('cloudresourcemanager', 'v1')
    # v2 only supports folder name resolution
    self.crm_v2 = discovery.build('cloudresourcemanager', 'v2')
    request = self.crm_v1.projects().list()
    tree = {}
    while request:
      response = request.execute()
      for project in response.get('projects', []):
        ancestry = self.get_ancestry_names(project["projectId"])
        # print(ancestry)
        if self.resolve:
          ancestry = self.resolve_ancestry(ancestry, project)
        tree = self.graft(tree, ancestry, project)
      request = self.crm_v1.projects().list_next(previous_request=request, previous_response=response)
    return tree
  
  def graft(self, tree, ancestry, metadata):
    branch = self.ancestry_branch(ancestry, metadata)
    return merge_or_raise.merge(tree, branch)
  
  def ancestry_branch(self, ancestry, metadata):
    res = {ancestry.pop(): metadata}
    while len(ancestry) > 0:
      res = {ancestry.pop(): res}
    return res
  
  def resolve_ancestry(self, ancestry, project):
    # TODO: Implement
    resolved = []
    for name in ancestry:
      if name.startswith("organizations"):
        response = self.crm_v1.organizations().get(name=name).execute()
      elif name.startswith("folders"):
        response = self.crm_v2.folders().get(name=name).execute()
      elif name.startswith("projects"):
        response = {'displayName': project['projectId']}
      resolved.append(response['displayName'])
    return resolved  
  
  def get_ancestry_names(self, project_id):
    response = self.crm_v1.projects().getAncestry(projectId=project_id).execute()
    return list(reversed([f"{i['resourceId']['type']}s/{i['resourceId']['id']}" for i in response["ancestor"]]))