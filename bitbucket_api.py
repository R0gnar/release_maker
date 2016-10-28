import json
from json.decoder import JSONDecodeError
from urllib.parse import urlencode
from tools import *
from settings import BITBUCKET_API_URL


class BitbucketApi:
    def __init__(self, login, password):
        self.authorization = make_basic_auth_str(login, password)

    def get_headers(self):
        return {
            'Authorization': 'Basic %s' % self.authorization,
            'Content-Type': 'application/json'
        }

    def get_projects(self):
        url = BITBUCKET_API_URL + 'projects?limit=1000'
        result = make_http_request(url, headers=self.get_headers())
        try:
            data = json.loads(result)
            return data['values']
        except JSONDecodeError:
            return []
        except KeyError:
            return []

    def get_project_repos(self, project):
        url = BITBUCKET_API_URL + 'projects/' + project + '/repos?limit=1000'
        result = make_http_request(url, headers=self.get_headers())
        try:
            data = json.loads(result)
            return data['values']
        except JSONDecodeError:
            return []
        except KeyError:
            return []

    def get_commits(self, project, repo, params):
        query = urlencode(params)
        url = BITBUCKET_API_URL + 'projects/' + project + '/repos/' + repo + '/commits?' + query
        result = make_http_request(url, headers=self.get_headers())
        try:
            data = json.loads(result)
            return data['values']
        except JSONDecodeError:
            return []
        except KeyError:
            return []
