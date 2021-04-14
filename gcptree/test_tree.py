import pytest
from .tree import Tree

class AncestryTestCase():
  def __init__(self, ancestry, expected):
    self.ancestry = ancestry
    self.expected = expected
  
  def test(self, inst):
    assert inst.ancestry_branch(self.ancestry, {}) == self.expected

class AncestryGraftTestCase():
  def __init__(self, ancestries, expected):
    self.ancestries = ancestries
    self.expected = expected
  
  def test(self, inst):
    tree = {}
    for ancestry in self.ancestries:
      tree = inst.graft(tree, ancestry, {})
    assert tree == self.expected

def test_ancestry_branch_with_one_layer():
  AncestryTestCase(
    ['organizations/1234', 'projects/a'],
    {'organizations/1234' : {'projects/a':{}}}
  ).test(Tree(""))

def test_ancestry_branch_with_two_layers():
  AncestryTestCase(
    ['organizations/1234', 'folders/1234', 'projects/a'],
    {'organizations/1234' : {'folders/1234': {'projects/a' : {}}}}
  ).test(Tree(""))

def test_ancestry_branch_with_three_layers():
  AncestryTestCase(
    ['organizations/1234', 'folders/1234', 'folders/5678', 'projects/a'],
    {'organizations/1234' : {'folders/1234': {'folders/5678' : {'projects/a': {}}}}}
  ).test(Tree(""))

def test_grafting_simple():
  ancestries = [
    ['organizations/1234', 'projects/a'],
    ['organizations/1234', 'projects/b']
  ]
  expected = {'organizations/1234': {'projects/a':{}, 'projects/b':{}}}
  AncestryGraftTestCase(ancestries, expected).test(Tree(""))

def test_grafting_two_layers():
  ancestries = [
    ['organizations/1234', 'projects/a'],
    ['organizations/1234', 'folders/123','projects/b']
  ]
  expected = {'organizations/1234': {'projects/a':{}, 'folders/123': {'projects/b':{}} }}
  AncestryGraftTestCase(ancestries, expected).test(Tree(""))
