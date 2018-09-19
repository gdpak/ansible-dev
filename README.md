# ansible-dev
Ansible Dev tools

## Installation:
```
sudo pip install https://github.com/gdpak/ansible-dev/archive/v1.1.tar.gz
```
## Example
1. Start an environment with ansible branch stable-2.6 and default python version
```
ansible-dev init -ver stable-2.6 <path>
```
2. Start another environment with ansible branch devel(default) and python 3
```
ansible-dev init <path> -py 3
```
3. Look at all the workspace created
```
ansible-dev ls -l
```
3. Change current workspace to work-on
```
ansible-dev workon <path>
```
4. Install a galaxy role in current workspace
```
ansible-dev update -r <galaxy_role_name>
e.g ansible-dev update -r ansible-network.cisco_ios
```
5. Install a role from github in current workspace
```
ansible-dev update -gr <github-repo-path>
e.g. ansible-dev update -gr https://github.com/gdpak/cisco_ios
```
6. Update existing role to latest released version
```
ansible-dev update -r ansible-network.cisco_ios --force
```

7. Create a playbook directory with all essential templates (inventory/vars etc)
```
ansible-dev create playbook foo
```

8. Create a role with all template direcory and files
```
ansible-dev create role foo_role
```

## Usage:
```
bash-3.2$ ansible-dev --help
Usage: ansible-dev [OPTIONS] COMMAND [ARGS]...

  ansible-dev is a command line tool for getting started with ansible. It
  does all prerequisite for running ansible and starts initial template for
  plalybook and roles

  See 'ansible-dev <command> --help' for more information on a specific
  command

Options:
  -v, --verbose  Enables verbose mode
  --help         Show this message and exit.

Commands:
  create  Create playbook/roles and other vars file to...
  init    Initialize the environment for ansible in a...
  ls      show details of ansible envionments
  update  Update existing workspace
  workon  set ansible workspace to work on Usage:...
```
