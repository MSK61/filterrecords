#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
extracts records identified by a filter file from a record file

Usage: filterRecords.py -f FILTERFILE [-o OUTFILE] RECORDFILE
"""

############################################################
#
# Copyright 2011 Mohammed El-Afifi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.
#
# program:      record filter
#
# file:         filterRecords.py
#
# function:     filtered record extractor
#
# description:  extracts records from a record file as specified by an
#                ID filter file
#
# author:       Mohammed Safwat (MS)
#
# environment:  emacs 23.2.1, python 2.6.5, windows xp professional
#
# notes:        This is a private program.
#
############################################################

import csv
import logging
from logging import debug, info
import sys
import optparse
# command-line option variables
# variable to receive the ID filter file
_FILTER_OPT_VAR = "filter_file_name"
# variable to receive the output file name
_OUT_OPT_VAR = "out_file_name"

def process_command_line(argv):
    """
    Return a 2-tuple: (settings object, args list).
    `argv` is a list of arguments, or `None` for ``sys.argv[1:]``.
    """
    if argv is None:
        argv = sys.argv[1:]

    # initialize the parser object:
    parser = optparse.OptionParser(
        "%prog -f FILTERFILE [-o OUTFILE] RECORDFILE", formatter=
        optparse.TitledHelpFormatter(width=78), add_help_option=None)

    # define options here:
    parser.add_option(      # ID filter file
        '-f', '--filter', dest=_FILTER_OPT_VAR,
        help="Use this file to filter records by ID's.")
    parser.add_option(      # filtered record output file
        '-o', '--output', dest=_OUT_OPT_VAR,
        help='Save the filtered records into this file.')
    parser.add_option(      # customized description; put --help last
        '-h', '--help', action='help',
        help='Show this help message and exit.')

    settings, args = parser.parse_args(argv)

    # check number of arguments:
    mandatoryArgs = 1
    extraArgs = len(args) - mandatoryArgs

    if extraArgs != 0:
        parser.error('program takes exactly one record file; ' +
                     (('"%s" ignored' % args[mandatoryArgs:]) if
                     extraArgs > 0 else "none specified") + '.')

    # further process settings
    # missing ID filter file
    if not getattr(settings, _FILTER_OPT_VAR):
        parser.error("ID filter file name not specified!")

    return settings, args

def main(argv=None):
    settings, args = process_command_line(argv)
    logging.basicConfig(level=logging.INFO)
    run(args[0], settings)
    return 0        # success


def run(rec_file, settings):
    """Filter the records from the input file.

    `rec_file` is the file containing records to be filtered.
    `settings` are the options for processing the input file.
    The function reads in the provided file containing records and
    generates a file containing only those records whose ID's exist in
    the ID filter file. The results are dumped to an output file.

    """
    # Process the file containing records.
    info("Reading record file %s...", rec_file)
    rec_map = {}
    rec_rd_permit = "rb"
    with open(rec_file, rec_rd_permit) as rec_list_file:

        rec_reader = csv.reader(rec_list_file)

        for rec in rec_reader:
            if rec:

                rec_map[rec[0]] = rec
                debug("Found record %s: %s", rec[0], rec)

            else:
                debug("Empty line encountered!")

    filter_file = getattr(settings, _FILTER_OPT_VAR)
    info("Finished reading record file %s, generating filtered list "
        "from ID filter file %s...", rec_file, filter_file)
    # Extract filtered records.
    out_file = getattr(settings, _OUT_OPT_VAR)
    wrt_permit = 'w'
    res_file = open(out_file, wrt_permit) if out_file else sys.stdout
    rec_wr_permit = "wb"
    out_rec_file = csv.writer(res_file)
    with open(filter_file) as filter_list:
        for id in filter_list:

            id = id.splitlines()[0]

            if id in rec_map:

                out_rec_file.writerow(rec_map[id])
                debug("Record %s extracted!", id)

            else:
                logging.warn("Unknown record %s encountered, skipping...", id)

    if out_file:
        res_file.close()

    info("Done!")


if __name__ == '__main__':
    status = main()
    sys.exit(status)
