#!/bin/bash

#######################################################
# Script to install OS packages defined in a dictionary
# Supports: Linux/Mac/Windows
# Author: Deepak Agrawal (deepacks@gmail.com)
# Licence: Apache
#######################################################

# Packages array "package_name:package_bin"
DEBIAN_PACKAGES_ARRAY=( "python:python"
                        "python-pip:pip"
                        "git:git" )

RHEL_PACKAGES_ARRAY=("python:python"
                     "python-pip:pip"
                     "git:git")

MACOS_PACKAGES_ARRAY=("python@2:python"
                      "git:git" )
MACOS_EASY_INSTALL_ARRAY=("pip:pip")

PIP_PACKAGES_ARRAY=( "virtualenv:virtualenv --version"
                     "ansible-dev:ansible-dev ls")


update_package_manager() {
    echo "Updating $1"
    update_pkg=`$1 -y update`
}

# arg1 : package_manger
# arg2 : package_name
# arg3 : pkg binary_name
# arg4 : command ('install/remove' ... )
install_a_package() {
    # Check if package bin is already installed
    pkg_installed="$($3 --version 2>&1)"
    re='not found'
    if [[ $pkg_installed =~ $re ]]; then
        echo "$4: $2 using $1"
        install_logs=`$1 $4 $2 -y`
        echo $install_logs
    else
        echo "$2 is already installed: $pkg_installed"
    fi
    return 1
}

install_packages() {
    local pkg_manager=$1
    local pkg_command=$2
    shift 2
    local pkg_array=("$@")
    for package in "${pkg_array[@]}" ; do
        pkg_name="${package%%:*}"
        pkg_bin="${package##*:}"
        install_a_package $pkg_manager $pkg_name $pkg_bin $pkg_command
    done
}

get_latest_release_ansible_dev() {
    ansible_dev_latest_release="$(\
        curl --silent "https://api.github.com/repos/gdpak/ansible-dev/releases/latest" | \
        grep '"tag_name":' | \
        sed -E 's/.*"([^"]+)".*/\1/')"
    ANSIBLE_DEV_TAR_BALL="https://github.com/gdpak/ansible-dev/archive/$ansible_dev_latest_release.tar.gz"
}

install_pip_packages() {
    for package in "${PIP_PACKAGES_ARRAY[@]}" ; do
        pkg_name="${package%%:*}"
        pkg_bin="${package##*:}"
        pkg_installed="$($pkg_bin 2>&1)"
        re='not found'
        if [[ $pkg_installed =~ $re ]]; then
            echo "Installing $pkg_name using pip"
            if [[ $pkg_name == "ansible-dev" ]]; then
                get_latest_release_ansible_dev
                install_logs=`pip install $ANSIBLE_DEV_TAR_BALL`
            else
                install_logs=`pip install $pkg_name`
                echo $install_logs
            fi
        else
            echo "$pkg_name is already installed: $pkg_installed"
        fi
    done
}

lowercase(){
    echo "$1" | sed "y/ABCDEFGHIJKLMNOPQRSTUVWXYZ/abcdefghijklmnopqrstuvwxyz/"
}

find_os_type() {
    OS=`lowercase \`uname\``
    local KERNEL=`uname -r`
    local MACH=`uname -m`

    if [ "{$OS}" == "windowsnt" ]; then
        OS=windows
    elif [ "{$OS}" == "darwin.*" ]; then
        OS=mac
    else
        OS=`uname`
        if [ "${OS}" = "SunOS" ] ; then
            OS=Solaris
            ARCH=`uname -p`
            OSSTR="${OS} ${REV}(${ARCH} `uname -v`)"
        elif [ "${OS}" = "AIX" ] ; then
            OSSTR="${OS} `oslevel` (`oslevel -r`)"
        elif [ "${OS}" = "Linux" ] ; then
            if [ -f /etc/redhat-release ] ; then
                DistroBasedOn='RedHat'
                DIST=`cat /etc/redhat-release |sed s/\ release.*//`
                PSUEDONAME=`cat /etc/redhat-release | sed s/.*\(// | sed s/\)//`
                REV=`cat /etc/redhat-release | sed s/.*release\ // | sed s/\ .*//`
            elif [ -f /etc/SuSE-release ] ; then
                DistroBasedOn='SuSe'
                PSUEDONAME=`cat /etc/SuSE-release | tr "\n" ' '| sed s/VERSION.*//`
                REV=`cat /etc/SuSE-release | tr "\n" ' ' | sed s/.*=\ //`
            elif [ -f /etc/mandrake-release ] ; then
                DistroBasedOn='Mandrake'
                PSUEDONAME=`cat /etc/mandrake-release | sed s/.*\(// | sed s/\)//`
                REV=`cat /etc/mandrake-release | sed s/.*release\ // | sed s/\ .*//`
            elif [ -f /etc/debian_version ] ; then
                DistroBasedOn='Debian'
                DIST=`cat /etc/lsb-release | grep '^DISTRIB_ID' | awk -F=  '{ print $2 }'`
                PSUEDONAME=`cat /etc/lsb-release | grep '^DISTRIB_CODENAME' | awk -F=  '{ print $2 }'`
                REV=`cat /etc/lsb-release | grep '^DISTRIB_RELEASE' | awk -F=  '{ print $2 }'`
            fi
            if [ -f /etc/UnitedLinux-release ] ; then
                DIST="${DIST}[`cat /etc/UnitedLinux-release | tr "\n" ' ' | sed s/VERSION.*//`]"
            fi
            OS=`lowercase $OS`
            DistroBasedOn=`lowercase $DistroBasedOn`
            readonly DIST
            readonly DistroBasedOn
            readonly PSUEDONAME
            readonly REV
            readonly KERNEL
            readonly MACH
        fi
    fi
    OS=`lowercase $OS`
    readonly OS
}


# Find OS type
find_os_type
echo "Found OS:$OS Distro:$DistroBasedOn"

PACKAGE_COMMAND='install'
PACKAGE_MANAGER=''
case $OS in
    linux)
        case $DistroBasedOn in
            debian)
                PACKAGE_MANAGER=apt-get
                update_package_manager $PACKAGE_MANAGER
                install_packages $PACKAGE_MANAGER $PACKAGE_COMMAND "${DEBIAN_PACKAGES_ARRAY[@]}"
                ;;
            redhat)
                #install epel on RHEL
                echo "Installing epel-repo for python-pip"
                eepl_install = "$(yum -y install epel-release 2>&1)"
                PACKAGE_MANAGER=yum
                install_packages $PACKAGE_MANAGER $PACKAGE_COMMAND "${RHEL_PACKAGES_ARRAY[@]}"
                ;;
            suse)
                echo "detected linux:suse distro. Using 'zypp' to install"
                PACKAGE_MANAGER=zypp
                ;;
            mandrake)
                echo "detected linux:suse distro. Using 'urpmi' to install"
                PACKAGE_MANAGER=urpmi
                ;;
            *)
                echo "unknown linux dist. exiting"
                ;;
        esac
        ;;
    darwin)
         # Check if brew is already installed
         brew_version=`brew --version`
         re='not found'
         if [[ $brew_version =~ $re ]]; then
             echo "Installing brew"
             brew_url='https://raw.githubusercontent.com/Homebrew/install/master/install'
             brew_install=$(/usr/bin/ruby -e "$(curl -fsSL $brew_url)" << "\r\n")
         else
             echo "Found installed brew: $brew_version"
         fi
         echo "MacOS: Using brew to install pyhon"
         PACKAGE_MANAGER='brew'
         update_package_manager $PACKAGE_MANAGER
         install_packages $PACKAGE_MANAGER $PACKAGE_COMMAND "${MACOS_PACKAGES_ARRAY[@]}"
         PACKAGE_MANAGER='easy_install'
         install_packages $PACKAGE_MANAGER "" "${MACOS_EASY_INSTALL_ARRAY[@]}"
         ;;
    *)
        echo "Unsupported OS. exiting ..."
        ;;
esac

# pip is now installed . Install ansible-dev from pip
install_pip_packages
echo "!! ansible-dev has been successfully Installed !!"
