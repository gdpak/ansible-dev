# ansible-dev
Ansible Dev tools

## Installation:

### Auto Installation
 Following script will install latest version of ansible-dev tool also it will
 install dependancies i.e. python, pip and virtualenv if not already installed

```
curl https://raw.githubusercontent.com/gdpak/ansible-dev/master/install.sh > install.sh
chmod 764 install.sh
sudo ./install.sh 
```

### Manual Installation

Please follow below links as per your OS

[Ubuntu](docs/debian/README.md) | [Centos/RHEL](docs/rhel/README.md) | [MacOS](docs/MacOS/README.md)

## Example

1. Start another environment with ansible branch devel(default)
```
ansible-dev init <path>
```
2. Start an environment with ansible branch stable-2.6 and default python version
```
ansible-dev init -ver stable-2.6 <path>
```
3. Look at all the workspace created
```
ansible-dev ls
```
4. Look at details of one workspace
```
ansible-dev ls -l <path>
```

5. Change current workspace to work-on
```
ansible-dev workon <path>
```
6. Install a galaxy role in current workspace
```
ansible-dev update -r <galaxy_role_name>
e.g ansible-dev update -r ansible-network.cisco_ios
```
7. Install a role from github in current workspace
```
ansible-dev update -gr <github-repo-path>
e.g. ansible-dev update -gr https://github.com/gdpak/cisco_ios
```
8. Update existing role to latest released version
```
ansible-dev update -r ansible-network.cisco_ios --force
```
9. Create a playbook directory with all essential templates (inventory/vars etc)
```
ansible-dev create playbook foo
```
10. Create a role with all template direcory and files
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
## Platforms tested

This tool does not have any OS specific code but there might be some pip, python related dependacies based on OS. It has been tested with automated scripts on below platforms

- CentOS/RHEL, 7.4
- Ubuntu, 16.04
- MacOSx, 10.13.6(High Sierra) [Installing virtualenv on mac](docs/MacOS/README.md)
