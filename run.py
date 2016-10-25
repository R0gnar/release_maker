#!/usr/bin/env python
import getpass
from tools import *
from jira_api import JiraApi
from bitbucket_api import BitbucketApi
import subprocess

print(styled('Release maker. Created by Dmitry Lysenkov.', bcolors.HEADER))

login = input_req('Логин Jira: ')
password = getpass.getpass()

jira_api = JiraApi(login, password)

permissions = jira_api.get_my_permissions()
if len(permissions) == 0:
    exit(styled('Нет доступа в Jira', bcolors.WARNING))


projects = jira_api.get_projects()
if len(projects) == 0:
    exit(styled('Нет доступных проектов', bcolors.WARNING))

print('Выберите проект')
for i in range(0, len(projects)):
    print(str(i) + ') ' + projects[i]['name'])

while True:
    project_key = int(input('Введите номер: '))
    if len(projects) > project_key >= 0:
        break

project = projects[project_key]
print(styled(project['name'], bcolors.BOLD))

versions = jira_api.get_project_versions(project['key'])
versions = [version for version in versions if not version['released']]
for i in range(0, len(versions)):
    print(str(i) + ') ' + versions[i]['name'])

if len(versions) > 1:
    while True:
        version_key = int(input('Введите номер: '))
        if len(versions) > version_key >= 0:
            break
    version = versions[version_key]
else:
    version = versions[0]

print(styled('Релиз ' + version['name'], bcolors.BOLD))

jql = 'project = ' + project['key'] + ' AND fixVersion = ' + version['name']
issues = jira_api.get_issues(jql)
if len(issues) == 0:
    exit(styled('Задачи релиза не найдены', bcolors.WARNING))

bitbucket_api = BitbucketApi(login, password)

projects = bitbucket_api.get_projects()
if len(projects) == 0:
    exit(styled('Проекты в bitbucket не найдены', bcolors.WARNING))

print('Выберите проект в Bitbucket:')
for i in range(0, len(projects)):
    print(str(i) + ') ' + projects[i]['name'])

while True:
    project_key = int(input('Введите номер: '))
    if len(projects) > project_key >= 0:
        break
    project = projects[project_key]

print(styled(project['name'], bcolors.BOLD))

repos = bitbucket_api.get_project_repos(project['key'])
if len(repos) == 0:
    exit(styled('Нет репозитариев в проекте'))

print('Выберите репозитарий')
for i in range(0, len(repos)):
    print(str(i) + ') ' + repos[i]['name'])

while True:
    repo_key = int(input('Введите номер: '))
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
    exit(styled('В выбранном репозитарии нет коммитов', bcolors.WARNING))


issue_keys = [issue['key'] for issue in issues]
release_commits = []
for commit in commits:
    valid = False
    try:
        for jira in commit['properties']['jira-key']:
            if jira in issue_keys:
                valid = True
    except KeyError:
        continue

    if valid:
        release_commits.append(commit['displayId'])


release_commits = list(reversed(release_commits))
subprocess.call(['git', 'checkout', 'master'])
subprocess.call(['git', 'pull', 'origin', 'master'])
branch = 'release/' + version['name']
subprocess.call(['git', 'branch', '-D', branch])
subprocess.call(['git', 'checkout', '-b', branch])
subprocess.call(['git', 'cherry-pick', '--ff'] + release_commits)
