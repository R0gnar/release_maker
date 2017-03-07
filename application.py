import getpass
import subprocess
import settings
from tools import bcolors, styled, input_list, input_req, print_table
from jira_api import JiraApi, JiraConnectionError, JiraError
from bitbucket_api import BitbucketApi, BitbucketConnectionError, BitbucketError
from commits_manager import CommitsManager


class Application:
    def __init__(self):
        self.login = None
        self.password = None
        self.jira_api = None
        self.bitbucket_api = None
        self.project = None
        self.bb_project = None
        self.repo = None
        self.fix_version = None

    def run(self):
        print(styled('Bitbucket tools', bcolors.HEADER))

        if settings.LOGIN and settings.PASSWORD:
            self.jira_login()

        if settings.PROJECT:
            self.select_jira_project()

        if settings.BITBUCKET_PROJECT:
            self.select_bitbucket_project()

        if settings.BITBUCKET_REPOSITORY:
            self.select_bitbucket_repo()

        while True:
            menu = self.get_menu()
            answer = self.show_menu(menu)
            menu[answer]['command']()

    def show_menu(self, menu):
        questions = [item['title'] for item in menu]
        answer = input_list(questions) - 1
        return answer

    def get_menu(self):
        menu = []
        if not self.jira_api:
            menu.append({
                'title': 'Login jira',
                'command': self.jira_login
            })

            return menu

        menu.append({
            'title': 'Make release branch',
            'command': self.make_release_branch
        })
        menu.append({
            'title': 'Work with current branch',
            'command': self.modify_current_branch
        })

        if self.project:
            title = 'Change jira project [' + self.project['key'] + ']'
        else:
            title = 'Select jira project'
        menu.append({
            'title': title,
            'command': self.select_jira_project
        })

        if self.bb_project:
            title = 'Change bitbucket project [' + self.bb_project['key'] + ']'
        else:
            title = 'Select bitbucket project'
        menu.append({
            'title': title,
            'command': self.select_bitbucket_project
        })

        if self.repo:
            title = 'Change bitbucket repository [' + self.repo['name'] + ']'
        else:
            title = 'Select bitbucket repository'
        menu.append({
            'title': title,
            'command': self.select_bitbucket_repo
        })

        menu.append({
            'title': 'Change jira login [' + self.login + ']'
        })

        return menu

    def jira_login(self):
        if not self.jira_api and settings.LOGIN and settings.PASSWORD:
            self.login = settings.LOGIN
            self.password = settings.PASSWORD
        else:
            self.login = input_req('Jira login: ')
            self.password = getpass.getpass()

        self.jira_api = JiraApi(self.login, self.password)
        self.bitbucket_api = BitbucketApi(self.login, self.password)

        try:
            permissions = self.jira_api.get_my_permissions()
        except JiraConnectionError:
            return self.error('Connection to jira failed')
        except JiraError:
            return self.error('Login or password is incorrect')
        else:
            if not permissions:
                return self.error('Jira permission denied')

    def select_jira_project(self):
        try:
            projects = self.jira_api.get_projects()
        except JiraConnectionError:
            return self.error('Connection to jira failed')
        except JiraError:
            return self.error('Projects not found')

        if len(projects) == 0:
            return self.error('Projects not found')

        project = None
        if not self.project and settings.PROJECT:
            project = [project for project in projects if project['key'] == settings.PROJECT]
            if project:
                project = project[0]

        if not project:
            print('Select project')
            answer = input_list([project['name'] for project in projects])
            project = projects[answer - 1]

        self.project = project

    def select_bitbucket_project(self):
        try:
            projects = self.bitbucket_api.get_projects()
        except BitbucketConnectionError:
            return self.error('Connection to bitbucket failed')
        except BitbucketError:
            return self.error('Projects in BitBucket not found')

        if len(projects) == 0:
            return self.error('Projects in BitBucket not found')

        project = None
        if not self.bb_project and settings.BITBUCKET_PROJECT:
            project = [project for project in projects if project['key'] == settings.BITBUCKET_PROJECT]
            if project:
                project = project[0]

        if not project:
            print('Select BitBucket project:')
            answer = input_list([project['name'] for project in projects])
            project = projects[answer - 1]

        self.bb_project = project
        self.repo = None

    def select_bitbucket_repo(self):
        if not self.bb_project:
            self.select_bitbucket_project()

        try:
            repos = self.bitbucket_api.get_project_repos(self.bb_project['key'])
        except BitbucketConnectionError:
            return self.error('Connection to bitbucket failed')
        except BitbucketError:
            return self.error('Repositories in selected project not found')

        if len(repos) == 0:
            return self.error('Repositories in selected project not found')

        repo = None
        if not self.repo and settings.BITBUCKET_REPOSITORY:
            repo = [repo for repo in repos if repo['name'] == settings.BITBUCKET_REPOSITORY]
            if repo:
                repo = repo[0]

        if not repo:
            print('Select repository')
            answer = input_list([repo['name'] for repo in repos])
            repo = repos[answer - 1]

        self.repo = repo

    def select_fix_version(self):
        if not self.project:
            self.select_jira_project()

        try:
            versions = self.jira_api.get_project_versions(self.project['key'])
        except JiraConnectionError:
            return self.error('Connection to jira failed')
        except JiraError:
            return self.error('Fix versions for selected project not found')

        if len(versions) == 0:
            return self.error('Fix versions for selected project not found')

        versions = [version for version in versions if not version['released']]
        answer = input_list([version['name'] for version in versions])
        version = versions[answer - 1]

        self.fix_version = version

    def make_release_branch(self):
        if not self.project or not self.bb_project or not self.repo:
            print(styled('Select jira project, bitbucket project and bitbucket repostiory', bcolors.ERROR))
            return

        self.select_fix_version()
        commits_controller = CommitsController(
            self.jira_api, self.bitbucket_api, self.project,
            self.bb_project, self.repo, self.fix_version
        )
        commits_controller.run()

    def modify_current_branch(self):
        if not self.project or not self.bb_project or not self.repo:
            print(styled('Select jira project, bitbucket project and bitbucket repostiory', bcolors.ERROR))
            return

        commits_controller = CommitsController(
            self.jira_api, self.bitbucket_api,
            self.bb_project, self.project, self.repo
        )
        commits_controller.run()

    def error(self, message):
        exit(styled(message, bcolors.ERROR))


class CommitsController:
    def __init__(self, jira_api, bitbucket_api, project, bb_project, repo, fix_version=None):
        self.project = project
        self.bb_project = bb_project
        self.repo = repo
        self.fix_version = fix_version
        self.jira_api = jira_api
        self.bitbucket_api = bitbucket_api
        self.commits_manager = CommitsManager()
        self.fix_version = fix_version
        self.branch_from = None
        self.branch_to = None

    def run(self):
        if self.fix_version:
            self.commits_manager.set_issues(self.get_fix_version_issues())
            self.branch_from = 'qa'
            self.branch_to = 'master'
        else:
            self.branch_from = input_req('Enter source branch: ')
            self.branch_to = input_req('Enter destination branch: ')

        self.commits_manager.set_commits(self.get_commits())

        while True:
            menu = self.get_menu()
            answer = self.show_menu(menu)
            result = menu[answer]['command']()
            if result is False:
                break

    def get_commits(self):
        params = {
            'until': self.branch_from,
            'since': self.branch_to,
            'merges': 'exclude',
            'limit': 10000
        }
        try:
            commits = self.bitbucket_api.get_commits(self.bb_project['key'], self.repo['slug'], params)
        except BitbucketConnectionError:
            exit(styled('Bitbucket connection failed', bcolors.ERROR))
            return False
        except BitbucketError:
            exit(styled('Commits not found', bcolors.ERROR))
            return False

        if len(commits) == 0:
            exit(styled('Commits in selected repository not found', bcolors.ERROR))
            return False

        return commits

    def get_fix_version_issues(self):
        jql = 'project = ' + self.project['key'] + ' AND fixVersion = ' + self.fix_version['name']
        issues = self.jira_api.get_issues(jql)
        if len(issues) == 0:
            exit(styled('Issues for selected fix version not found', bcolors.ERROR))
            return False

        return issues

    def get_menu(self):
        menu = list()
        menu.append({
            'title': 'Show issue commits count',
            'command': self.show_issue_commits_count
        })
        menu.append({
            'title': 'Show commits',
            'command': self.show_commits
        })
        menu.append({
            'title': 'Add commit',
            'command': self.add_commit
        })
        menu.append({
            'title': 'Remove commit',
            'command': self.remove_commit
        })
        menu.append({
            'title': 'Add jira issue',
            'command': self.add_issue
        })
        menu.append({
            'title': 'Remove jira issue',
            'command': self.remove_issue
        })
        menu.append({
            'title': 'Start cherry-pick',
            'command': self.cherry_pick
        })

        return menu

    def show_menu(self, menu):
        questions = [item['title'] for item in menu]
        answer = input_list(questions) - 1
        return answer

    def show_issue_commits_count(self):
        issues_commits = self.commits_manager.get_issues_commits_count()
        table_data = [['Jira issue', 'Count']]
        for jira in issues_commits:
            table_data.append([
                jira,
                issues_commits[jira]
            ])

        print_table(table_data)

    def show_commits(self):
        commits = self.commits_manager.get_available_commits()
        table_data = [['ID', 'Message', 'Author']]
        for commit in commits:
            table_data.append([
                commit['displayId'],
                commit['message'],
                commit['author']['name']
            ])

        print_table(table_data)

    def add_commit(self):
        commit = input('Enter commit id: ')
        self.commits_manager.add_allowed_commit(commit)

    def remove_commit(self):
        commit = input('Enter commit id: ')
        self.commits_manager.add_disable_commit(commit)

    def add_issue(self):
        issue_key = input('Enter issue key: ')
        try:
            issue = self.jira_api.get_issue(issue_key)
        except JiraConnectionError:
            print(styled('Jira connection error', bcolors.ERROR))
        except JiraError:
            print(styled('Issue not found', bcolors.ERROR))
        else:
            self.commits_manager.add_issue(issue)

    def remove_issue(self):
        issue_key = input('Enter issue key: ')
        try:
            issue = self.jira_api.get_issue(issue_key)
        except JiraConnectionError:
            print(styled('Jira connection error', bcolors.ERROR))
        except JiraError:
            print(styled('Issue not found', bcolors.ERROR))
        else:
            self.commits_manager.remove_issue(issue)

    def cherry_pick(self):
        subprocess.call(['git', 'cherry-pick', '--abort'])
        subprocess.call(['git', 'fetch'])
        if self.fix_version:
            branch = 'release/' + self.fix_version['name']
            answer = input(styled('WARNING! Your local branch ' + branch + ' was deleted [y/n]', bcolors.WARNING))
            if answer != 'y' and answer != 'Y':
                return

            subprocess.call(['git', 'checkout', 'master'])
            subprocess.call(['git', 'pull', 'origin', 'master'])
            subprocess.call(['git', 'branch', '-D', branch])
            subprocess.call(['git', 'checkout', '-b', branch])
        else:
            answer = input(styled('WARNING! Cherry-pick apply for current branch [y/n]', bcolors.WARNING))
            if answer != 'y' and answer != 'Y':
                return

        release_commits = list(reversed(self.commits_manager.get_available_commits_ids()))
        subprocess.call(['git', 'cherry-pick', '--ff'] + release_commits)
        exit()
