#!/bin/bash

#######################################################
# Script to install OS packages defined in a dictionary
# Supports: Linux/Mac/Windows
# Author: Deepak Agrawal (deepacks@gmail.com)
# Licence: Apache
#######################################################

# Packages array "package_name:package_bin"
DEBIAN_PACKAGES_ARRAY=( "python:python"
                        "python-pip:pip" )

RHEL_PACKAGES_ARRAY=("python:python"
                     "python-pip:pip")

MACOS_PACKAGES_ARRAY=("python@2:python")
MACOS_EASY_INSTALL_ARRAY=("pip:pip")

update_package_manager() {
    echo "Updating $1"
    update_pkg=`$1 update`
}

# arg1 : package_manger
# arg2 : package_name
# arg3 : pkg binary_name
# arg4 : command ('install/remove' ... )
install_a_package() {
    # Check if package bin is already installed
    echo "checking $3"
    pkg_installed=`$3 --version`
    re='not found'
    if [[ $pkg_installed =~ $re ]]; then
        echo "$4: $2 using $1"
        install_logs=`$1 $4 $2`
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
                PACKAGE_MANAGER=yum
                update_package_manager $PACKAGE_MANAGER
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
