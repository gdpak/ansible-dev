## Installing python, pip and virtualenv on MacOS 

one of the easiest way is to install though brew

1. Install homebrew with the command:
```
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```
2. Install Python
```
brew install python
```
Permission errors ? Do this:
```
sudo chown -R "$USER":admin /usr/local
sudo chown -R "$USER":admin /Library/Caches/Homebrew
```

3. brew installs python as python@2 and python@3. so make an alias for python as
   python2 or python3

   open ~/.bashrc and put below command
```
alias python='python2'
```

4. Install pip 
```
sudo easy_install pip
```

5. Install virtualenv
```
sudo pip install virtualenv
```

