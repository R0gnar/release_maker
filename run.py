#!/usr/bin/env python3
import getpass
import subprocess
from tools import *
from jira_api import JiraApi
from bitbucket_api import BitbucketApi
from commits_manager import CommitsManager

print(styled('Release maker. Created by Dmitry Lysenkov.', bcolors.HEADER))

login = input_req('Jira login: ')
password = getpass.getpass()

jira_api = JiraApi(login, password)

permissions = jira_api.get_my_permissions()
if len(permissions) == 0:
    exit(styled('Login or password is incorrect', bcolors.WARNING))


projects = jira_api.get_projects()
if len(projects) == 0:
    exit(styled('Projects not found', bcolors.WARNING))

print('Select project')
answer = input_list([project['name'] for project in projects])
project = projects[answer - 1]
print(styled(project['name'], bcolors.BOLD))

versions = jira_api.get_project_versions(project['key'])
if len(versions) == 0:
    exit(styled('Fix versions for selected project not found'))

versions = [version for version in versions if not version['released']]
answer = input_list([version['name'] for version in versions])
version = versions[answer - 1]
print(styled('Selected fix version ' + version['name'], bcolors.BOLD))

jql = 'project = ' + project['key'] + ' AND fixVersion = ' + version['name']
issues = jira_api.get_issues(jql)
if len(issues) == 0:
    exit(styled('Issues for selected fix version not found', bcolors.WARNING))

bitbucket_api = BitbucketApi(login, password)

projects = bitbucket_api.get_projects()
if len(projects) == 0:
    exit(styled('Projects in BitBucket not found', bcolors.WARNING))

print('Select BitBucket project:')
answer = input_list([project['name'] for project in projects])
project = projects[answer - 1]
print(styled(project['name'], bcolors.BOLD))

repos = bitbucket_api.get_project_repos(project['key'])
if len(repos) == 0:
    exit(styled('Repositories in selected project not found'))

print('Select repository')
answer = input_list([repo['name'] for repo in repos])
repo = repos[answer - 1]
print(styled(repo['name'], bcolors.BOLD))

params = {
    'until': 'qa',
    'since': 'master',
    'merges': 'exclude',
    'limit': 10000
}
commits = bitbucket_api.get_commits(project['key'], repo['slug'], params)
if len(commits) == 0:
    exit(styled('Commits in selected repository not found', bcolors.WARNING))

commits_manager = CommitsManager()
commits_manager.set_commits(commits)
commits_manager.set_release_issues(issues)
commits_manager.print_release_issues_commits_count()

while True:
    answer = input_list([
        'Show release commits',
        'Add commit to release',
        'Delete commit from release',
        'Make release branch'
    ])

    if answer == 1:
        commits_manager.print_release_commits()
    elif answer == 2:
        commit_id = input_req('Enter commit id: ')
        commits_manager.add_allowed_commit(commit_id)
    elif answer == 3:
        commit_id = input_req('Enter commit id:')
        commits_manager.add_disable_commit(commit_id)
    elif answer == 4:
        break

subprocess.call(['git', 'fetch'])
subprocess.call(['git', 'checkout', 'master'])
subprocess.call(['git', 'pull', 'origin', 'master'])
branch = 'release/' + version['name']
subprocess.call(['git', 'branch', '-D', branch])
subprocess.call(['git', 'checkout', '-b', branch])
release_commits = reversed(commits_manager.get_release_commits_ids())
subprocess.call(['git', 'cherry-pick', '--ff'] + commits_manager.get_release_commits_ids())
