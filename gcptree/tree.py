from googleapiclient import discovery
from deepmerge import merge_or_raise
import json
import os
from .cache import Cache

class Tree():
  PROJECT_TYPE="cloudresourcemanager.googleapis.com/Project"
  # Disable all the no-member violations in this class
  # pylint: disable=no-member
  def __init__(self, org_id, full_resource=False, cache_inst=None):
    self.org = "organizations/{}".format(org_id)
    self.full_resource = full_resource
    self.crm = discovery.build('cloudresourcemanager', 'v3')
    self.cai = discovery.build('cloudasset','v1p5beta1')
    self.cache = Cache()
    if cache_inst:
      self.cache = cache_inst
    self.should_update_cache = False

  def build(self):
    if self.cache.is_empty():
      return self.build_while_caching()
    tree = {}
    for p in self.cache.get('projects'):
      ancestry, project = self.resolve_ancestry(reversed(p['ancestors']))
      if self.full_resource:
          ancestry = list(reversed(p['ancestors']))
      tree = self.graft(tree, ancestry, project)
    return tree

  def build_while_caching(self):
    request = self.cai.assets().list(parent=self.org, assetTypes=[self.PROJECT_TYPE])
    tree = {}
    projects_to_cache = []
    while request:
      response = request.execute()
      for p in response.get('assets', []):
        projects_to_cache.append(p)
        ancestry, project = self.resolve_ancestry(reversed(p['ancestors']))
        if self.full_resource:
          ancestry = list(reversed(p['ancestors']))
        tree = self.graft(tree, ancestry, project)
      request = self.cai.assets().list_next(previous_request=request, previous_response=response)
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
  
  def resolve_ancestry(self, ancestry):
    project_metadata = None
    resolved = []
    for name in ancestry:
      if self.cache.has(name):
        entry = self.cache.get(name)
        if name.startswith("projects"):
          project_metadata = entry
          resolved.append(entry['projectId'])
        else:
          resolved.append(entry)
      else:
        response = {}
        if name.startswith("organizations"):
          response = self.crm.organizations().get(name=name).execute()
          self.cache.add(name, response['displayName'])
          resolved.append(response['displayName'])
        elif name.startswith("folders"):
          response = self.crm.folders().get(name=name).execute()
          self.cache.add(name, response['displayName'])
          resolved.append(response['displayName'])
        elif name.startswith("projects"):
          response = self.crm.projects().get(name=name).execute()
          project_metadata = response
          self.cache.add(name, response)
          resolved.append(response['projectId'])
    return resolved, project_metadata
