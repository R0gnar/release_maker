import json
from json.decoder import JSONDecodeError
from urllib.parse import urlencode
from tools import make_basic_auth_str, make_http_request
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
        if not result:
            raise BitbucketConnectionError

        try:
            data = json.loads(result)
            projects = data['values']
        except (JSONDecodeError, KeyError):
            raise BitbucketError
        else:
            return projects

    def get_project_repos(self, project):
        url = BITBUCKET_API_URL + 'projects/' + project + '/repos?limit=1000'
        result = make_http_request(url, headers=self.get_headers())
        if not result:
            raise BitbucketConnectionError

        try:
            data = json.loads(result)
            repositories = data['values']
        except (JSONDecodeError, KeyError):
            raise BitbucketError
        else:
            return repositories

    def get_commits(self, project, repo, params):
        query = urlencode(params)
        url = BITBUCKET_API_URL + 'projects/' + project + '/repos/' + repo + '/commits?' + query
        result = make_http_request(url, headers=self.get_headers())
        if not result:
            raise BitbucketConnectionError

        try:
            data = json.loads(result)
            commits = data['values']
        except (JSONDecodeError, KeyError):
            raise BitbucketError
        else:
            return commits


class BitbucketError(Exception):
    pass


class BitbucketConnectionError(BitbucketError):
    pass
