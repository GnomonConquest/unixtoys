#!/usr/bin/env python
# encoding: utf-8
'''
ddstats -- system stat collector without decoration

ddstats is a system stat collector that does not try to generate pretty tables

This script wraps psutil and takes command line switches for output control.
The ddstats.py script is a cross-platform toy that does what I wanted sysstat
to do in the first place.

@author:     Dimitry Dukhovny

@copyright:  2018 Dimitry Dukhovny. All rights reserved.

@license:    GNU General Public License, version 3

@contact:    dimitry <AT> dukhovny <DOT> net
@deffield    updated: 20180620

If TESTRUN=1 and you are running this as a script,
 __name__ should be '__main__' as below...

>>> __name__
'__main__'
'''

import sys
import os
import psutil
import traceback
from time import sleep

from optparse import OptionParser

__all__ = []
__version__ = 0.4
__date__ = '2018-06-20'
__updated__ = '2018-06-20'

DEBUG = 0
TESTRUN = 0
PROFILE = 0


WIN32 = False
if os.name == 'nt':
    WIN32 = True


def OUTPUT(outstring):
    '''Sends text to stdout with a carriage return.
    >>> OUTPUT('mystring')
    mystring
    '''
    outstring = str(outstring)
    sys.stdout.write(outstring + '\n')


def OUTERR(outstring):
    '''Sends text to stderr with a carriage return.  Stdout should get nothing.
    >>> OUTERR('mystring')
    '''
    outstring = str(outstring)
    sys.stderr.write(outstring + '\n')


def sizeof_fmt(num, suffix='B'):
    '''Human-printable value generator stolen from Fred Cirera in 2007.
    >>> sizeof_fmt(2893749120834)
    '2.6TB'
    '''
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Y', suffix)


def totalcpu():
    '''Returns a float percent of CPU utilization from a one-second
    snapshot.
    >>> type(totalcpu())
    <type 'float'>
    '''
    return(psutil.cpu_percent(1, False))


def eachcpu():
    '''Returns a list CPU utilization percentages for each CPU in order.
    >>> type(eachcpu())
    <type 'list'>
    '''
    return(psutil.cpu_percent(1, True))


def ramused():
    '''Returns a float percent of RAM utilization.
    >>> type(ramused())
    <type 'float'>
    '''
    return(psutil.virtual_memory().percent)


def ramratio():
    '''Returns an array ['x', 'y'] of x memory in use and y total memory.
    >>> type(ramratio())
    <type 'list'>
    '''
    ram = psutil.virtual_memory()
    return([sizeof_fmt(ram.total - ram.available), sizeof_fmt(ram.total)])


def totaldiskio(sample_interval=5):
    '''Takes a sample_interval in seconds and returns transactions per second.
    This includes reads and writes from all disks.
    >>> type(totaldiskio(0.01))
    <type 'float'>
    '''
    diskio1 = psutil.disk_io_counters(perdisk=False)
    sleep(sample_interval)
    diskio2 = psutil.disk_io_counters(perdisk=False)
    t = (diskio2.read_count + diskio2.write_count - diskio1.read_count -
         diskio1.write_count)
    return(float(t)/float(sample_interval))


def eachdiskio(sample_interval=5):
    '''Returns a dictionary of { 'N': x } for each disk N and x transactions
    per second.
    >>> type(eachdiskio(0.01))
    <type 'dict'>
    '''
    outdict = {}
    diskio1 = psutil.disk_io_counters(perdisk=True)
    sleep(sample_interval)
    diskio2 = psutil.disk_io_counters(perdisk=True)
    if diskio1.keys() != diskio2.keys():
        return(None)
    for disk in diskio2.keys():
        t = (diskio2[disk].read_count + diskio2[disk].write_count -
             diskio1[disk].read_count - diskio1[disk].write_count)
        outdict.update({disk: float(t)/float(sample_interval)})
    return(outdict)


def fetchdiskspace(partitionobject):
    '''Gets the disk usage from an object returned by psutil.disk_partition().
    It returns a key-value pair of the partition name and its percentage of use
    or the last exception thrown in the attempt.
    >>> type(fetchdiskspace(psutil.disk_partitions()[0]))
    <type 'dict'>
    '''
    try:
        k = partitionobject.device
    except:
        k = 'UnknownDevice'
    try:
        v = psutil.disk_usage(partitionobject.mountpoint).percent
    except:
        v = -1
    return({k: v})


def eachdiskspace():
    '''Returns a dictionary of { 'N': x } for each device N and x percent of
    disk consumed, eliminating redundancies.
    >>> type(eachdiskspace())
    <type 'dict'>
    '''
    diskdict = {}
    map(lambda x: diskdict.update(fetchdiskspace(x)), psutil.disk_partitions())
    return(diskdict)


def processcount():
    '''Returns number of running processes.
    >>> type(processcount())
    <type 'int'>
    '''
    return(len(psutil.pids()))


def uniqueprocesscount(processlist=[]):
    '''Returns number of unique process names.
    >>> type(uniqueprocesscount())
    <type 'int'>
    '''
    if not processlist:
        processlist = psaux()
    unique_procs = len(set(map(lambda x: x.name(), processlist)))
    return(unique_procs)


def fhcount(processlist=[]):
    '''Returns number of unique process names.
    >>> type(fhcount())
    <type 'int'>
    '''
    if not processlist:
        processlist = psaux()
    try:
        if WIN32:
            fhcounter = sum(map(lambda x: x.num_handles(), processlist))
        else:
            fhcounter = sum(map(lambda x: x.num_fds(), processlist))
    except:
        fhcounter = 'Unknown.  Maybe you need more privileges.'
    return(fhcounter)


def psaux():
    '''Get process list by either new or old means.  This is for backward
    compatibility to old or <gasp>Win32</gasp> versions of psutil.
    >>> type(psaux()[0])
    <class 'psutil.Process'>
    '''
    try:
        outlist = psutil.get_process_list()
    except:
        try:
            outlist = list(psutil.process_iter())
        except:
            outlist = []
    return(outlist)


def main(argv=None):
    '''Command line options parsing.  Takes arrays and returns an integers.
    >>> main([])
    0
    '''
    program_name = os.path.basename(sys.argv[0])
    program_version = __version__
    program_build_date = "%s" % __updated__

    program_version_string = '%%prog %s (%s)' % (program_version,
                                                 program_build_date)
    program_longdesc = '''Print stripped-down system stats.'''
    program_license = '''Copyright 2018 Dimitry Dukhovny Licensed under the
    GNU General Public License, version 3
    https://www.gnu.org/licenses/gpl.txt'''

    if argv is None:
        argv = sys.argv[1:]
    try:
        # setup option parser
        parser = OptionParser(version=program_version_string,
                              epilog=program_longdesc,
                              description=program_license)
        parser.add_option("-v", "--verbose", dest="verbose",
                          action="store_true",
                          help="set verbosity level \
                          [default: %default]")
        parser.add_option("-l", "--label", dest="label", action="store_true",
                          help="add INI-style labels to output \
                          [default: %default]")
        parser.add_option("-t", "--interval", dest="sample_interval",
                          action="store", type="int",
                          help="Set the interval for polling disk IO. \
                          [default: %default]")
        parser.add_option("-u", "--cpu", dest="cpu", action="store_true",
                          help="Get total CPU utilization \
                          or per-CPU if verbose")
        parser.add_option("-m", "--memory", dest="memory", action="store_true",
                          help="Get total memory utilization \
                          or ratio if verbose")
        parser.add_option("-d", "--disk", dest="disk", action="store_true",
                          help="Get per-device disk utilization")
        parser.add_option("-i", "--diskio", dest="diskio", action="store_true",
                          help="Get total transactions per second \
                          for a specified interval or per-disk if verbose")
        parser.add_option("-p", "--procs", dest="procs", action="store_true",
                          help="Get process count \
                          or compare unique process count \
                          to total if verbose.")
        parser.add_option("-f", "--filehandles", dest="handles",
                          action="store_true",
                          help="Get number of open file handles.  \
                          Usually requires privilege escalation.")
        parser.add_option("-a", "--all", dest="all", action="store_true",
                          help="Perform all of the above checks.  \
                          Usually requires privilege escalation.")

        # set defaults
        parser.set_defaults(verbose=False)
        parser.set_defaults(label=False)
        parser.set_defaults(sample_interval=5)
        parser.set_defaults(cpu=False)
        parser.set_defaults(memory=False)
        parser.set_defaults(disk=False)
        parser.set_defaults(diskio=False)
        parser.set_defaults(procs=False)
        parser.set_defaults(handles=False)
        parser.set_defaults(all=False)

        # process options
        (opts, args) = parser.parse_args(argv)
        if args:
            sys.argv.append['-h']

        # reusables
        processlist = []

        # Handling our flags
        if opts.cpu or opts.all:
            if opts.label:
                OUTERR('\n[CPU]')
            OUTPUT(totalcpu())
            if opts.verbose:
                OUTPUT(totalcpu())
        if opts.memory or opts.all:
            if opts.label:
                OUTERR('\n[MEMORY]')
            if opts.verbose:
                ratio = ramratio()
                OUTPUT(ratio[0] + ' / ' + ratio[1])
            else:
                OUTPUT(str(ramused()))
        if opts.disk or opts.all:
            if opts.label:
                OUTERR('\n[DISK]')
            diskstatus = eachdiskspace()
            for disk in diskstatus.keys():
                OUTPUT(disk + ' :  ' + str(diskstatus[disk]))
        if opts.diskio or opts.all:
            if opts.label:
                OUTERR('\n[DISKIO]')
            if opts.verbose or opts.all:
                diskstatus = eachdiskio(opts.sample_interval)
                for disk in diskstatus.keys():
                    OUTPUT(disk + ' :  ' + str(diskstatus[disk]))
            else:
                OUTPUT(totaldiskio(opts.sample_interval))
        if opts.procs or opts.all:
            if opts.label:
                OUTERR('\n[PROCESSES]')
            if opts.verbose:
                if not processlist:
                    processlist = psaux()
                OUTPUT(str(uniqueprocesscount(processlist)) +
                       ' unique from a total of ' + str(processcount()))
            else:
                OUTPUT(processcount())
        if opts.handles or opts.all:
            if opts.label:
                OUTERR('\n[HANDLES]')
            if not processlist:
                processlist = psaux()
            OUTPUT(fhcount(processlist))

        # MAIN BODY #

    except Exception, e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help\n")
        print(traceback.format_exc())
        return 2

    return 0


if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-h")
    if TESTRUN:
        import doctest
        doctest.testmod(verbose=True)
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'ddstats_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())
