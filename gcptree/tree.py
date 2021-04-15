from googleapiclient import discovery
from deepmerge import merge_or_raise
import json
import os
from .cache import Cache

class Tree():
  # Disable all the no-member violations in this class
  # pylint: disable=no-member
  def __init__(self, org_id, full_resource=False):
    self.org = f"organizations/{org_id}"
    self.resolve = not full_resource
    self.cache = Cache()

  def build(self):
    if self.cache.is_empty():
      return self.build_while_caching()
    tree = {}
    for project in self.cache.get('projects'):
      ancestry = self.get_ancestry_names(project["projectId"])
      if self.resolve:
        ancestry = [self.cache.get(name) for name in ancestry]
      tree = self.graft(tree, ancestry, project)
    return tree

  def build_while_caching(self):
    # v1 is the only version that supports project ancestry
    self.crm_v1 = discovery.build('cloudresourcemanager', 'v1')
    # v2 only supports folder name resolution
    self.crm_v2 = discovery.build('cloudresourcemanager', 'v2')
    request = self.crm_v1.projects().list()
    tree = {}
    projects_to_cache = []
    while request:
      response = request.execute()
      for project in response.get('projects', []):
        projects_to_cache.append(project)
        ancestry = self.get_ancestry_names(project["projectId"])
        if self.resolve:
          ancestry = self.resolve_ancestry(ancestry, project)
        tree = self.graft(tree, ancestry, project)
      request = self.crm_v1.projects().list_next(previous_request=request, previous_response=response)
    self.cache.add("projects", projects_to_cache)
    self.cache.write()
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
    resolved = []
    for name in ancestry:
      if name.startswith("organizations"):
        response = self.crm_v1.organizations().get(name=name).execute()
      elif name.startswith("folders"):
        response = self.crm_v2.folders().get(name=name).execute()
      elif name.startswith("projects"):
        response = {'displayName': project['projectId']}
      self.cache.add(name, response['displayName'])
      resolved.append(response['displayName'])
    return resolved

  def get_ancestry_names(self, project_id):
    cache_key = f"ancestry/{project_id}"
    if self.cache.has(cache_key):
      return self.cache.get(cache_key)
    response = self.crm_v1.projects().getAncestry(projectId=project_id).execute()
    names = list(reversed([f"{i['resourceId']['type']}s/{i['resourceId']['id']}" for i in response["ancestor"]]))
    self.cache.add(cache_key, names)
    return names