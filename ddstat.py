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
@deffield    updated: 20180619
'''

import sys
import os
import psutil
import traceback
from time import sleep

from optparse import OptionParser

__all__ = []
__version__ = 0.2
__date__ = '2018-06-19'
__updated__ = '2018-06-19'

DEBUG = 0
TESTRUN = 0
PROFILE = 0


def OUTPUT(outstring):
    outstring = str(outstring)
    sys.stdout.write(outstring + '\n')

def OUTERR(outstring):
    outstring = str(outstring)
    sys.stderr.write(outstring + '\n')

def sizeof_fmt(num, suffix='B'):
    '''Human-printable value generator stolen from Fred Cirera in 2007.'''
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Y', suffix)


def totalcpu():
    '''Returns a float percent of CPU utilization from a one-second
    snapshot.'''
    return(psutil.cpu_percent(1, False))


def eachcpu():
    '''Returns a list CPU utilization percentages for each CPU in order.'''
    return(psutil.cpu_percent(1, True))


def ramused():
    '''Returns a float percent of RAM utilization.'''
    return(psutil.virtual_memory().percent)


def ramratio():
    '''Returns an array ['x', 'y'] of x memory in use and y total memory.'''
    ram = psutil.virtual_memory()
    return([sizeof_fmt(ram.total - ram.available), sizeof_fmt(ram.total)])


def totaldiskio(sample_interval=5):
    '''Takes a sample_interval in seconds and returns transactions per second.
    This includes reads and writes from all disks.'''
    diskio1 = psutil.disk_io_counters(perdisk=False)
    sleep(sample_interval)
    diskio2 = psutil.disk_io_counters(perdisk=False)
    t = (diskio2.read_count + diskio2.write_count - diskio1.read_count 
         - diskio1.write_count)
    return(float(t)/float(sample_interval))


def eachdiskio(sample_interval=5):
    '''Returns a dictionary of { 'N': x } for each disk N and x transactions
    per second.'''
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


def eachdiskspace():
    '''Returns a dictionary of { 'N': x } for each device N and x percent of
    disk consumed, eliminating redundancies.'''
    diskdict = {}
    map(lambda x: 
        diskdict.update(
            {x.device: psutil.disk_usage(x.mountpoint).percent}
            ),
         psutil.disk_partitions())
    return(diskdict)


def main(argv=None):
    '''Command line options.'''

    program_name = os.path.basename(sys.argv[0])
    program_version = "v0.1"
    program_build_date = "%s" % __updated__

    program_version_string = '%%prog %s (%s)' % (program_version, program_build_date)
    program_longdesc = '''Print stripped-down system stats.'''
    program_license = '''Copyright 2018 Dimitry Dukhovny 
      Licensed under the GNU General Public License, 
      version 3 https://www.gnu.org/licenses/gpl.txt'''

    if argv is None:
        argv = sys.argv[1:]
    try:
        # setup option parser
        parser = OptionParser(version=program_version_string, epilog=program_longdesc, description=program_license)
        parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                          help="set verbosity level [default: %default]")
        parser.add_option("-l", "--label", dest="label", action="store_true",
                          help="add INI-style labels to output [default: %default]")
        parser.add_option("-t", "--interval", dest="sample_interval", action="store", type="int",
                          help="Set the interval for polling disk IO. [default: %default]")
        parser.add_option("-u", "--cpu", dest="cpu", action="store_true",
                          help="Get total CPU utilization or per-CPU if verbose")
        parser.add_option("-m", "--memory", dest="memory", action="store_true",
                          help="Get total memory utilization or ratio if verbose")
        parser.add_option("-d", "--disk", dest="disk", action="store_true",
                          help="Get per-device disk utilization")
        parser.add_option("-i", "--diskio", dest="diskio", action="store_true",
                          help="Get total transactions per second for a specified interval or per-disk if verbose")

        # set defaults
        parser.set_defaults(verbose=False)
        parser.set_defaults(label=False)
        parser.set_defaults(sample_interval=5)
        parser.set_defaults(cpu=False)
        parser.set_defaults(memory=False)
        parser.set_defaults(disk=False)
        parser.set_defaults(diskio=False)

        # process options
        (opts, args) = parser.parse_args(argv)

        if opts.cpu:
            if opts.label:
                OUTERR('\n[CPU]')
            OUTPUT(totalcpu())
            if opts.verbose:
                OUTPUT(totalcpu())
        if opts.memory:
            if opts.label:
                OUTERR('\n[MEMORY]')
            if opts.verbose:
                ratio = ramratio()
                OUTPUT(ratio[0] + ' / ' + ratio[1])
            else:
                OUTPUT(str(ramused()))
        if opts.disk:
            if opts.label:
                OUTERR('\n[DISK]')
            diskstatus = eachdiskspace()
            for disk in diskstatus.keys():
                OUTPUT(disk + ' :  ' + str(diskstatus[disk]))
        if opts.diskio:
            if opts.label:
                OUTERR('\n[DISKIO]')
            if opts.verbose:
                diskstatus = eachdiskio(opts.sample_interval)
                for disk in diskstatus.keys():
                    OUTPUT(disk + ' :  ' + str(diskstatus[disk]))
            else:
                OUTPUT(totaldiskio(opts.sample_interval))

        # MAIN BODY #

    except Exception, e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help\n")
        print(traceback.format_exc())
        return 2


if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-h")
    if TESTRUN:
        import doctest
        doctest.testmod()
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
