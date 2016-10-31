from tools import print_table


class CommitsManager:
    def __init__(self):
        self._commits = []
        self._issues = []
        self._allowed_commits = []
        self._disable_commits = []

    def set_commits(self, commits):
        self._commits = commits

    def add_commit(self, commit):
        self._commits.append(commit)

    def set_issues(self, issues):
        self._issues = issues

    def add_issue(self, issue):
        search = [item for item in self._issues if item['key'] == issue['key']]
        if not search:
            self._issues.append(issue)

    def remove_issue(self, issue):
        for i in range(0, len(self._issues)):
            if self._issues[i]['key'] == issue['key']:
                del self._issues[i]

    def get_issues_keys(self):
        return [issue['key'] for issue in self._issues]

    def add_allowed_commit(self, commit):
        if commit in self._disable_commits:
            self._disable_commits.remove(commit)

        self._allowed_commits.append(commit)

    def add_disable_commit(self, commit):
        if commit in self._allowed_commits:
            self._allowed_commits.remove(commit)

        self._disable_commits.append(commit)

    def get_available_commits(self):
        release_commits = list()
        for commit in self._commits:
            if self.is_valid_commit(commit):
                release_commits.append(commit)

        return release_commits

    def get_available_commits_ids(self):
        return [commit['displayId'] for commit in self.get_available_commits()]

    def get_issues_commits_count(self):
        issues_commits = {}
        for issue in self._issues:
            issues_commits[issue['key']] = 0

        for commit in self.get_available_commits():
            try:
                for jira in commit['properties']['jira-key']:
                    if jira not in issues_commits:
                        issues_commits[jira] = 0

                    issues_commits[jira] += 1
            except KeyError:
                pass

        return issues_commits

    def is_valid_commit(self, commit):
        if commit['id'] in self._allowed_commits or commit['displayId'] in self._allowed_commits:
            return True

        if commit['id'] in self._disable_commits or commit['displayId'] in self._disable_commits:
            return False

        valid = False
        try:
            for jira in commit['properties']['jira-key']:
                if jira in self.get_issues_keys():
                    valid = True
                    break
        except KeyError:
            pass

        return valid
