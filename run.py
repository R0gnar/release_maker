#!/usr/bin/env python
import getpass
from tools import *
from jira_api import JiraApi
from bitbucket_api import BitbucketApi
import subprocess
import math

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
for i in range(0, len(projects)):
    print(str(i) + ') ' + projects[i]['name'])

while True:
    project_key = int(input('Enter number: '))
    if len(projects) > project_key >= 0:
        break

project = projects[project_key]
print(styled(project['name'], bcolors.BOLD))

versions = jira_api.get_project_versions(project['key'])
if len(versions) == 0:
    exit(styled('Fix versions for selected project not found'))

versions = [version for version in versions if not version['released']]
for i in range(0, len(versions)):
    print(str(i) + ') ' + versions[i]['name'])

while True:
    version_key = int(input('Enter number: '))
    if len(versions) > version_key >= 0:
        break

version = versions[version_key]
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
for i in range(0, len(projects)):
    print(str(i) + ') ' + projects[i]['name'])

while True:
    project_key = int(input('Enter number: '))
    if len(projects) > project_key >= 0:
        break
    project = projects[project_key]

print(styled(project['name'], bcolors.BOLD))

repos = bitbucket_api.get_project_repos(project['key'])
if len(repos) == 0:
    exit(styled('Repositories in selected project not found'))

print('Select repository')
for i in range(0, len(repos)):
    print(str(i) + ') ' + repos[i]['name'])

while True:
    repo_key = int(input('Enter number: '))
    if len(repos) > repo_key >= 0:
        break

repo = repos[repo_key]
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


issue_keys = [issue['key'] for issue in issues]
release_commits = []
commits_count = {}
for commit in commits:
    valid = False
    try:
        for jira in commit['properties']['jira-key']:
            if jira in issue_keys:
                if jira not in commits_count:
                    commits_count[jira] = 0

                valid = True
                commits_count[jira] += 1
    except KeyError:
        continue

    if valid:
        release_commits.append(commit['id'])

print(styled('Release commits count:', bcolors.HEADER))
print('-' * 49)
print('|' + ' ' * 6 + 'Jira issue' + ' ' * 7 + '|' + ' ' * 5 + 'Commits count' + ' ' * 5 + '|')
print('-' * 49)
for jira in commits_count:
    count = commits_count[jira]
    jlspace = int(math.ceil((23 - len(jira)) / 2))
    jrspace = int(math.floor((23 - len(jira)) / 2))

    count = str(count)
    clspace = int(math.ceil((23 - len(count)) / 2))
    crspace = int(math.floor((23 - len(count)) / 2))

    print('|' + ' ' * jlspace + jira + ' ' * jrspace + '|' + ' ' * clspace + count + ' ' * crspace + '|')
    print('-' * 49)

release_commits = list(reversed(release_commits))
approve = input_req("Make release branch uses this commits [y/n]?\n")
if approve == 'n' or approve == 'N':
    exit(styled('Making release branch canceled', bcolors.WARNING))

subprocess.call(['git', 'fetch'])
subprocess.call(['git', 'checkout', 'master'])
subprocess.call(['git', 'pull', 'origin', 'master'])
branch = 'release/' + version['name']
subprocess.call(['git', 'branch', '-D', branch])
subprocess.call(['git', 'checkout', '-b', branch])
subprocess.call(['git', 'cherry-pick', '--ff'] + release_commits)
