from github import Github
from base64 import b64decode
import json 
from types import SimpleNamespace

# using an access token
g = Github("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")

for repo in g.get_user().get_repos():
    if repo.name == 'Ip_List_For_Libraries':
        repo = repo
        break

ip = '192.168.1.146'
city = ''

contents = repo.get_contents("ip-list.json", ref="main")
print(str(b64decode(contents.content))[2:-1])
file_content = json.loads(str(b64decode(contents.content))[2:-1])
last = f"{int(list(file_content.keys())[-1])+1}"
print(last)
file_content.update({last : ''})
file_content[last] = {
    'IP' : '192.168.1.146',
    'City' : 'Novotroitsk'
}
repo.update_file(contents.path, "more", json.dumps(file_content), contents.sha, branch="main")