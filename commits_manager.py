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

    def set_release_issues(self, issues):
        self._issues = issues

    def get_issues_keys(self):
        return [issue['key'] for issue in self._issues]

    def add_allowed_commit(self, commit):
        self._allowed_commits.append(commit)

    def add_disable_commit(self, commit):
        self._disable_commits.append(commit)

    def get_release_commits(self):
        release_commits = list()
        for commit in self._commits:
            if self.is_valid_commit(commit):
                release_commits.append(commit)

        return release_commits

    def get_release_commits_ids(self):
        return [commit['id'] for commit in self.get_release_commits()]

    def print_release_commits(self):
        commits = self.get_release_commits()
        table_data = [['ID', 'Message', 'Author']]
        for commit in commits:
            table_data.append([
                commit['displayId'],
                commit['message'],
                commit['author']['name']
            ])

        print_table(table_data)

    def get_release_issues_commits_count(self):
        issues_commits = {}
        for issue in self._issues:
            issues_commits[issue['key']] = 0

        for commit in self.get_release_commits():
            try:
                for jira in commit['properties']['jira-key']:
                    if jira not in issues_commits:
                        issues_commits[jira] = 0

                    issues_commits[jira] += 1
            except KeyError:
                pass

        return issues_commits

    def print_release_issues_commits_count(self):
        issues_commits = self.get_release_issues_commits_count()
        table_data = [['Jira issue', 'Count']]
        for jira in issues_commits:
            table_data.append([
                jira,
                issues_commits[jira]
            ])

        print_table(table_data)

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
