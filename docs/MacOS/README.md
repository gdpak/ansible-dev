## Install ansible-dev using pip
Install current latest released branch (v1.1.0)
```
sudo pip install https://github.com/gdpak/ansible-dev/archive/v1.1.0.tar.gz
```
## OPTIONAL (if python, pip and virtualenv are not already installed)

one of the easiest way is to install though brew

- Install homebrew with the command:
```
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```
- Install Python
```
brew install python
```
Permission errors ? Do this:
```
sudo chown -R "$USER":admin /usr/local
sudo chown -R "$USER":admin /Library/Caches/Homebrew
```
- brew installs python as python@2 and python@3. so make an alias for python as python2 or python3

open ~/.bashrc and put below command
```
alias python='python2'
```
- Install pip 
```
sudo easy_install pip

- Install virtualenv
```
sudo pip install virtualenv
```
