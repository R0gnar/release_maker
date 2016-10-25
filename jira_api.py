from tools import *
import json
from json.decoder import JSONDecodeError
from urllib.parse import urlencode
from settings import JIRA_API_URL


class JiraApi:
    def __init__(self, login, password):
        self.authorization = make_basic_auth_str(login, password)

    def get_headers(self):
        return {
            'Authorization': 'Basic %s' % self.authorization,
            'Content-Type': 'application/json'
        }

    def get_my_permissions(self):
        url = JIRA_API_URL + 'mypermissions'
        result = make_http_request(url, headers=self.get_headers())
        try:
            data = json.loads(result)
            return data['permissions']
        except JSONDecodeError:
            return []
        except KeyError:
            return []
        except TypeError:
            return []

    def get_projects(self):
        url = JIRA_API_URL + 'project'
        result = make_http_request(url, headers=self.get_headers())
        try:
            return json.loads(result)
        except JSONDecodeError:
            return []

    def get_project_versions(self, project_key):
        url = JIRA_API_URL + 'project/' + project_key + '/versions'
        result = make_http_request(url, headers=self.get_headers())
        try:
            return json.loads(result)
        except JSONDecodeError:
            return []

    def get_issues(self, jql):
        url = JIRA_API_URL + 'search'
        query = urlencode({
            'jql': jql
        })

        result = make_http_request(url + '?' + query, headers=self.get_headers())
        try:
            data = json.loads(result)
            return data['issues']
        except JSONDecodeError:
            return []
        except KeyError:
            return []
