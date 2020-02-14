import requests
import pydot
import os
import json
import sys
import base64
import time
from collections import namedtuple
from pprint import pprint
from random import randint
from github3 import GitHub
from urllib.parse import urlparse

graph = pydot.Dot(graph_type="graph", rankdir="UD")

def add(graph, root, children):
    for child in children:
        edge = pydot.Edge(root,child)
        graph.add_edge(edge)

def enhance_metadata(reponame:str, orgname:str,token:str,sdlc_steps:{}) ->{}:
    """ searches repos in the org defined
        finds the metadata files and fetches them
        returns metadata files groupped by sdlc step
    """
    data = gather_metadata(reponame=reponame,orgname=orgname,token=token)
    for dat in data:
        for step in dat.get('sdlc', None):
            sdlc_steps[step].append(dat)
    return sdlc_steps

def add_file_to_graph(filename:str):
    """
    parses the file and based on the values defined in the named tuple above
    appends project info to the relevant part of the mind map
    """
    json.load(filename)

def gather_metadata(reponame:str, orgname:str,token:str) ->[]:
    """Builds the repo object for every repo in the org
    :param options the settings object
    :returns list of type Helper containing repo objects with repo url, clone url and options for each object
    """
    result = []
    connection = GitHub(token=token)
    org_metadata_files = connection.search_code("org:%s filename:*.json path:/"%orgname)
    repo_metadata_file = connection.search_code("repo:%s, filename:*.json path:/"%reponame)
    #TODO(@northdpole): this can be done using *_metadata_file.extend()
    for f in org_metadata_files:
        time.sleep(1)
        content = requests.get(f.url)
        if content.status_code == 200:
            resp = json.loads(content.text)
            metadata = json.loads(base64.b64decode(resp['content']))
            result.append(metadata)
        else:
            print("ERROR response code: %s"%content.status_code)
    for f in repo_metadata_file:
        time.sleep(1)
        content = requests.get(f.url)
        if content.status_code == 200:
            resp = json.loads(content.text)
            metadata = json.loads(base64.b64decode(resp['content']))
            result.append(metadata)
        else:
            print("ERROR response code: %s"%content.status_code)
    return result

mindmap = {"SDLC":{"Planning":{},"Analysis":{},"Design":{},"Implementation":{},"Maintenance":{},"Strategy":{},"Culture":{}}}

orgs = {"owasp":"owasp", "zap":"zap"} # this should eventually be a json or some other easily parsable file mapping repos to projects
repos = {"":""}
metadata = {}
for human_org_name,github_org_name in orgs:
    metadata = enhance_metadata(orgname=github_org_name,token=sys.argv[1])

for human_repo_name,github_repo_name in repos:
    metadata = enhance_metadata(reponame=github_repo_name,token=sys.argv[1],metadata=metadata)

# TODO(@northdpole): validate metadata can actually be appended, perhaps it makes sense to see how this would look like with an example org and repos :-)
# TODO (@northdpole): make the expected values in info.json an object with ENUMS for fields
# TODO (@northdpole): make this script not burn the eyes of everyone who looks at it.



for key,value in mindmap.items():
    add(graph, key,value.keys())
    if isinstance(value, dict):
        for step,items in value.items():
            add(graph, step,items)
graph.write_png("map.png")
os.stat("map.png")
