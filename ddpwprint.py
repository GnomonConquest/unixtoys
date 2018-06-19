#!/usr/bin/python

# Title:   ddpwprint.py
# Source:  Dimitry Dukhovny dimitry <at> dukhovny <dot> net
# History: 20171220.1822Z:  Added commandline switches, piped input,
#              and password generator
#          20170404.1838Z:  Initial version
# Purpose: Print (usually passwords) in phonetics to correct for font
#               problems.
# License: GPL
#          Source code and original attribution must be
#               distributed, even if the original source was
#               modified.  No commercial redistribution for
#               trade, sale, or barter permitted without the
#               permission of the author.

import sys
import re


phoneticascii = {
    chr(32): 'space',
    chr(33): 'exclamation_mark',
    chr(34): 'double_quote',
    chr(35): 'number',
    chr(36): 'dollar',
    chr(37): 'percent',
    chr(38): 'ampersand',
    chr(39): 'single_quote',
    chr(40): 'left_parenthesis',
    chr(41): 'right_parenthesis',
    chr(42): 'asterisk',
    chr(43): 'plus',
    chr(44): 'comma',
    chr(45): 'minus',
    chr(46): 'period',
    chr(47): 'slash',
    chr(48): 'zero',
    chr(49): 'one',
    chr(50): 'two',
    chr(51): 'three',
    chr(52): 'four',
    chr(53): 'five',
    chr(54): 'six',
    chr(55): 'seven',
    chr(56): 'eight',
    chr(57): 'nine',
    chr(58): 'colon',
    chr(59): 'semicolon',
    chr(60): 'less_than',
    chr(61): 'equality_sign',
    chr(62): 'greater_than',
    chr(63): 'question_mark',
    chr(64): 'at_sign',
    chr(65): 'upper_alpha',
    chr(66): 'upper_bravo',
    chr(67): 'upper_charlie',
    chr(68): 'upper_delta',
    chr(69): 'upper_echo',
    chr(70): 'upper_foxtrot',
    chr(71): 'upper_golf',
    chr(72): 'upper_hotel',
    chr(73): 'upper_india',
    chr(74): 'upper_juliet',
    chr(75): 'upper_kilo',
    chr(76): 'upper_lima',
    chr(77): 'upper_mike',
    chr(78): 'upper_november',
    chr(79): 'upper_oscar',
    chr(80): 'upper_papa',
    chr(81): 'upper_quebec',
    chr(82): 'upper_romeo',
    chr(83): 'upper_sierra',
    chr(84): 'upper_tango',
    chr(85): 'upper_uniform',
    chr(86): 'upper_victor',
    chr(87): 'upper_whiskey',
    chr(88): 'upper_xray',
    chr(89): 'upper_yankee',
    chr(90): 'zulu',
    chr(91): 'left_bracket',
    chr(92): 'backslash',
    chr(93): 'right_bracket',
    chr(94): 'caret',
    chr(95): 'underscore',
    chr(96): 'grave',
    chr(97): 'alpha',
    chr(98): 'bravo',
    chr(99): 'charlie',
    chr(100): 'delta',
    chr(101): 'echo',
    chr(102): 'foxtrot',
    chr(103): 'golf',
    chr(104): 'hotel',
    chr(105): 'india',
    chr(106): 'juliet',
    chr(107): 'kilo',
    chr(108): 'lima',
    chr(109): 'mike',
    chr(110): 'november',
    chr(111): 'oscar',
    chr(112): 'papa',
    chr(113): 'quebec',
    chr(114): 'romeo',
    chr(115): 'sierra',
    chr(116): 'tango',
    chr(117): 'uniform',
    chr(118): 'victor',
    chr(119): 'whiskey',
    chr(120): 'xray',
    chr(121): 'yankee',
    chr(122): 'zulu',
    chr(123): 'left_brace',
    chr(124): 'vertical_bar',
    chr(125): 'right_brace',
    chr(126): 'tilde'
    }


def phonetic(inchar=''):
    '''Tries to return a phonetic value from the ASCII dictionary.  Returns
    an empty string if you feed it an unprintable character.'''
    inchar = str(inchar)
    try:
        return(phoneticascii[inchar])
    except:
        return('')


def getphonetic(intext):
    '''Validates intext and iterates over it with phonetic().'''
    try:
        intext = str(intext)
    except:
        sys.stderr.write('Your input isn\'t a string.  Sorry.\n')
        return(False)
    outtext = map(phonetic, intext)
    return(outtext)


def printphonetic(intext):
    '''Iterates over intext.  Anything set off in quotes is treated as one
    entry, unless you escape the quotes.'''
    sys.stdout.write('\n--\nPassword:  ' + intext + '\n')
    outtext = getphonetic(intext)
    if outtext:
        map(lambda x:  sys.stdout.write('         ' + x + '\n'), outtext)
        return(True)
    else:
        return(False)

def main(argv=[None]):
    map(printphonetic, argv[1:])
    map(printphonetic, sys.stdin)

if __name__ == '__main__':
    main(sys.argv)
