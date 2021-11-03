from github import Github
from base64 import b64decode

# using an access token
g = Github("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")

for repo in g.get_user().get_repos():
    if repo.name == 'Ip_List_For_Libraries':
        repo = repo
        break

ip = ''
city = ''

contents = repo.get_contents("ip-list.txt", ref="main")
file_content = str(b64decode(contents.content))[2:-1]
file_content = file_content + f'|{ip}|{city}|'
#file_content.replace('||', '|').split('|')[1:-1]
repo.update_file(contents.path, "more", file_content, contents.sha, branch="main")