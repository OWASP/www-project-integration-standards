from github3 import GitHub
import unittest
import pydot
from owasp_project_metadata_mindmap_gen import build_graph, build_metadata,Info, gather_metadata
from tempfile import mktemp
from pprint import pprint
from unittest.mock import patch
from collections import namedtuple

class TestProjMetadataParsers(unittest.TestCase):
 
    def setUp(self):
        self.data ={'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA': [{"name": "northdpole/testRepo2",
                                                             "repository": "https://github.com/northdpole/standaloneTestRepo1",
                                                             "tags": ["defenders", "foo", "bar"],
                                                             "sdlc": ["AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", "Cooking"],
                                                             "example_usage": "get hammer -> smash drives -> ignite thermite",
                                                             "output_type": ["smashed drives"]}],
 'Analysis': [{"name": "testOrg/testRepo1",
  "repository": "https://github.com/testOrgForMetadataScript/testRepo1",
   "tags": ["builders", "foo", "bar"],
    "sdlc": ["Analysis", "Implementation"],
     "example_usage": "https://demo.testOrg.testRepo1.org",
      "output_type": ["urls", "guidelines"]},
             {"name": "testOrg/testRepo2",
              "repository": "https://github.com/testOrgForMetadataScript/testRepo2",
               "tags": ["breakers", "positive", "test"],
                "sdlc": ["Analysis", "Culture"],
                 "example_usage": "docker run -v /tmp:/tmp foobar:v1.3",
                  "output_type": ["type"]}],
 'Cooking': [{"name": "northdpole/testRepo2", 
 "repository": "https://github.com/northdpole/standaloneTestRepo1", 
 "tags": ["defenders", "foo", "bar"],
  "sdlc": ["AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", "Cooking"],
   "example_usage": "get hammer -> smash drives -> ignite thermite",
    "output_type": ["smashed drives"]}],
 'Culture': [{"name": "testOrg/testRepo2",
  "repository": "https://github.com/testOrgForMetadataScript/testRepo2",
   "tags": ["breakers", "positive", "test"],
    "sdlc": ["Analysis", "Culture"],
     "example_usage": "docker run -v /tmp:/tmp foobar:v1.3",
      "output_type": ["type"]}],
 'Design': [],
 'Implementation': [{"name": "testOrg/testRepo1",
  "repository": "https://github.com/testOrgForMetadataScript/testRepo1", 
  "tags": ["builders", "foo", "bar"], "sdlc": ["Analysis", "Implementation"], 
  "example_usage": "https://demo.testOrg.testRepo1.org", 
  "output_type": ["urls", "guidelines"]}],

 'Maintenance': [],
 'Planning': [],
 'Strategy': [{"name": "northdpole/standaloneTestRepo2",
  "repository": "https://github.com/northdpole/standaloneTestRepo2", 
  "tags": ["builders", "positive", "test"], 
  "sdlc": ["Strategy"],
   "example_usage": "kubectl delete po --all --all-namespaces", 
   "output_type": ["destruction"]}]}

        self.metadata = {}
        for k, vals in self.data.items():
            self.metadata[k] = []
            for v in vals:
                self.metadata[k].append(Info(v))

    def test_build_graph(self):
        self.maxDiff= None
        test_graph = build_graph(self.metadata)
        tmp_graph = mktemp()
        test_graph.write(tmp_graph)
    
        with open("test_data/map.dot") as f1, open(tmp_graph) as f2:
            graph = f1.read()
            generated_graph = f2.read()
            
        self.assertEqual(graph,generated_graph)

    @patch('owasp_project_metadata_mindmap_gen.enhance_metadata')
    def test_build_metadata(self,mocked_enhance):
        mocked_enhance.return_value = self.metadata
        org_dict = {"testOrgForMetadataScript":"testOrgForMetadataScript","owasp":"owasp", "zap":"zap"}
        repo_dict = {"standaloneTestRepo1":"northdpole/standaloneTestRepo1","standaloneTestRepo2":"northdpole/standaloneTestRepo2"}

        self.assertEqual(self.metadata, build_metadata(org_dict,repo_dict))
    
    @patch('github3.GitHub')
    @patch('github3.GitHub.search_code')
    @patch('requests.get')
    def test_gather_metadata(self,patched_requests,patched_search_code,patched_github):
        search_res = namedtuple("SearchRes","url")
        requests_obj = namedtuple("Reqs",["status_code","text"])

        patched_search_code.return_value= [search_res(url="https://foo.bar.baz")]
        patched_requests.return_value = requests_obj(status_code=200,text= '{"name":"info.json","path":"info.json","sha":"12940ba7e1aff97a9d756663664042165fa70ea3","size":303,"url":"https://api.github.com/repos/testOrgForMetadataScript/testRepo1/contents/info.json?ref=aef89606c1a9223b86d000a2c3a34c5b3d1dbae7","html_url":"https://github.com/testOrgForMetadataScript/testRepo1/blob/aef89606c1a9223b86d000a2c3a34c5b3d1dbae7/info.json","git_url":"https://api.github.com/repos/testOrgForMetadataScript/testRepo1/git/blobs/12940ba7e1aff97a9d756663664042165fa70ea3","download_url":"https://raw.githubusercontent.com/testOrgForMetadataScript/testRepo1/aef89606c1a9223b86d000a2c3a34c5b3d1dbae7/info.json","type":"file","content":"CnsiaW5mbyIgOiB7CiAgICAibmFtZSI6InRlc3RPcmcvdGVzdFJlcG8xIiwK\\nICAgICJyZXBvc2l0b3J5IjoiaHR0cHM6Ly9naXRodWIuY29tL3Rlc3RPcmdG\\nb3JNZXRhZGF0YVNjcmlwdC90ZXN0UmVwbzEiLAogICAgInRhZ3MiOlsiYnVp\\nbGRlcnMiLCJmb28iLCJiYXIiXSwKICAgICJzZGxjIjpbIkFuYWx5c2lzIiwi\\nSW1wbGVtZW50YXRpb24iXSwKICAgICJleGFtcGxlX3VzYWdlIjoiaHR0cHM6\\nLy9kZW1vLnRlc3RPcmcudGVzdFJlcG8xLm9yZyIsCiAgICAib3V0cHV0X3R5\\ncGUiOlsidXJscyIsImd1aWRlbGluZXMiXQogICAgfQp9\\n","encoding":"base64","_links":{"self":"https://api.github.com/repos/testOrgForMetadataScript/testRepo1/contents/info.json?ref=aef89606c1a9223b86d000a2c3a34c5b3d1dbae7","git":"https://api.github.com/repos/testOrgForMetadataScript/testRepo1/git/blobs/12940ba7e1aff97a9d756663664042165fa70ea3","html":"https://github.com/testOrgForMetadataScript/testRepo1/blob/aef89606c1a9223b86d000a2c3a34c5b3d1dbae7/info.json"}}')
        
        metadata = [{'info': {'example_usage': 'https://demo.testOrg.testRepo1.org',
           'name': 'testOrg/testRepo1',
           'output_type': ['urls', 'guidelines'],
           'repository': 'https://github.com/testOrgForMetadataScript/testRepo1',
           'sdlc': ['Analysis', 'Implementation'],
           'tags': ['builders', 'foo', 'bar']}}]

        self.assertEqual(metadata,gather_metadata(None,"orgname"))
        patched_search_code.assert_called_with("org:orgname filename:info.json path:/")
        patched_requests.assert_called_with("https://foo.bar.baz")


        self.assertEqual(metadata,gather_metadata("reponame",None))
        patched_search_code.assert_called_with("repo:reponame filename:info.json path:/")
        pass
    
    @unittest.skip('todo')
    def test_enhance_metadata(self):
        pass


if __name__ == '__main__':
    unittest.main()