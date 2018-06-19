#!/bin/bash

# Title:   ddsshcheck.sh
# Source:  Dimitry Dukhovny dimitry <at> dukhovny <dot> net
# History: 20170426.1934Z:  Initial version
# Purpose: Check if the local SSH config is safe.  Written as an instructional
#          script to help a colleague learn bash while making something useful.

# Show usage information
dohelp() {
    echo "I do not know what key check you want. My parameters are 1, 2, or 3."
    echo " 1:  Checks /root/.ssh and /home/*/.ssh for bad keyfiles."
    echo " 2:  Checks everywhere for .ssh directories with bad keyfiles."
    echo " 3:  Checks everywhere for bad keyfiles."
}


# Report on common expected values in ssd_config. See output text for
#  further explanation.
reportsshd() {
    filename=${1:-/etc/ssh/sshd_config}
    echo "-=[ Checking ${filename} ]=-"
    danger='^\s*Protocol\s*1'
    message=" DANGER:  Protocol 1 is unsafe!"
    [ `egrep -c ${danger} ${filename}` -gt 0 ] && echo ${message}
    danger='^\s*UsePrivilegeSeparation\s*no'
    message=" DANGER:  UsePrivilegeSeparation should be yes"
    [ `egrep -c ${danger} ${filename}` -gt 0 ] && echo ${message}
    danger='^\s*PermitRootLogin\s*yes'
    message=" DANGER:  PermitRootLogin should be no"
    [ `egrep -c ${danger} ${filename}` -gt 0 ] && echo ${message}
    danger='^\s*IgnoreRhosts\s*no'
    message=" DANGER:  IgnoreRhosts should be yes"
    [ `egrep -c ${danger} ${filename}` -gt 0 ] && echo ${message}
    danger='^\s*PermitEmptyPasswords\s*yes'
    message=" DANGER:  PermitEmptyPasswords should be no"
    [ `egrep -c ${danger} ${filename}` -gt 0 ] && echo ${message}
    danger='^\s*AllowTcpForwarding\s*yes'
    message=" NOTICE:  AllowTcpForwarding is yes; this is OK"
    [ `egrep -c ${danger} ${filename}` -gt 0 ] && echo ${message}
    danger='^\s*GatewayPorts\s*yes'
    message=' DANGER:  GatewayPorts should be no'
    [ `egrep -c ${danger} ${filename}` -gt 0 ] && echo ${message}
    #danger='^\s*'
    #message='DANGER:  '
    #[ `egrep -c ${danger} ${filename}` -gt 0 ] && echo ${message}
    echo " Nothing further to report."
}
    
    
# Report the condition of keys by checking if a file is an SSH key and
#  ensuring it is encrypted.
reportkeys() {
    target=${1:-${HOME}/.ssh}
    if [ -d ${target} ]
    then
        candidates=`find ${target} -type f -exec grep -l 'SA PRIVATE KEY-' {} \; | \
            xargs -i egrep -Hoc ENCRYPTED {} | \
            egrep ':0$' | \
            perl -pe 's/:.$//'`
        for c in ${candidates}
        do
            if [ `ssh-keygen -P - -yf ${c} 2>&1 | grep -ic 'incorrect passphrase'` -ne 1 ]
            then
                echo ${c}
            fi
        done
    fi
}


# This is where we start with commandline parameters.
main() {
    intensive=${1:-0}
    [ ${EUID} -ne 0 ] && echo "You are rootless!" && exit 1
    # Start by checking sshd_config, no matter what.
    reportsshd
    # This should have been a case statement.
    if [ ${intensive} -eq 1 2> /dev/null ]
    then
        echo "-=[ Checking the usual locations for bad key files. ]=-"
        echo "-=[ This will be quick. ]=-"
        for target in /root/.ssh `find /home -xdev -type d -name \.ssh`
        do
            reportkeys ${target}
        done
    elif [ ${intensive} -eq 2 2> /dev/null ]
    then {
        echo "-=[ Checking everywhere for .ssh directories with bad keyfiles. ]=-"
        echo "-=[ This will take a little while. ]=-"
        for target in /root/.ssh `find /home -xdev -type d -name \.ssh`
        do
            reportkeys ${target}
        done
    }
    elif [ ${intensive} -eq 3 2> /dev/null ]
    then {
        echo "-=[ Checking every file on your file system for unsecure keys. ]=-"
        echo "-=[ This will take a very long time. ]=-"
        reportkeys /
    }
    else dohelp
    fi
}

main ${@}
