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

def fetch_metadata(orgname:str,token:str):
    """ searches repos in the org defined
        finds the metadata files and fetches them
        returns metadata files groupped by sdlc step
    """
    data = gather_metadata(orgname,token)
    sdlc_steps = {}
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

def gather_metadata(orgname:str,token:str) ->[]:
    """Builds the repo object for every repo in the org
    :param options the settings object
    :returns list of type Helper containing repo objects with repo url, clone url and options for each object
    """
    result = []
    connection = GitHub(token=token)
    metadata_files = connection.search_code("org:owasp filename:*.json path:/")
    for f in metadata_files:
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


metadata = fetch_metadata("owasp",sys.argv[1])

for key,value in mindmap.items():
    add(graph, key,value.keys())
    if isinstance(value, dict):
        for step,items in value.items():
            add(graph, step,items)
graph.write_png("map.png")
os.stat("map.png")

