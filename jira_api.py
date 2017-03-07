import json
from json.decoder import JSONDecodeError
from urllib.parse import urlencode
from settings import JIRA_API_URL
from tools import make_basic_auth_str, make_http_request


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
        if not result:
            raise JiraConnectionError

        try:
            data = json.loads(result)
            permissions = data['permissions']
        except (JSONDecodeError, KeyError, TypeError):
            raise JiraError
        else:
            return permissions

    def get_projects(self):
        url = JIRA_API_URL + 'project'
        result = make_http_request(url, headers=self.get_headers())
        if not result:
            raise JiraConnectionError

        try:
            return json.loads(result)
        except JSONDecodeError:
            raise JiraError

    def get_project_versions(self, project_key):
        url = JIRA_API_URL + 'project/' + project_key + '/versions'
        result = make_http_request(url, headers=self.get_headers())
        if not result:
            raise JiraConnectionError

        try:
            return json.loads(result)
        except JSONDecodeError:
            raise JiraError

    def get_issues(self, jql):
        url = JIRA_API_URL + 'search'
        query = urlencode({
            'jql': jql
        })

        result = make_http_request(url + '?' + query, headers=self.get_headers())
        if not result:
            raise JiraConnectionError

        try:
            data = json.loads(result)
            issues = data['issues']
        except (JSONDecodeError, KeyError):
            raise JiraError
        else:
            return issues

    def get_issue(self, key):
        url = JIRA_API_URL + 'issue/' + key

        result = make_http_request(url, headers=self.get_headers())
        if not result:
            raise JiraConnectionError

        try:
            issue = json.loads(result)
        except JSONDecodeError:
            raise JiraError
        else:
            return issue


class JiraError(Exception):
    pass


class JiraConnectionError(JiraError):
    pass
