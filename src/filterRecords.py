#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
extracts records identified by a filter file from a record file

Usage: filterRecords.py [OPTION...] RECORDFILE
"""

############################################################
#
# Copyright 2011, 2012 Mohammed El-Afifi
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
#               ID filter file
#
# author:       Mohammed Safwat (MS)
#
# environment:  emacs 23.2.1, python 2.6.5, windows xp professional
#               KWrite 4.6.5, python 2.7.1, Fedora release 15 (Lovelock)
#               KWrite 4.7.4, python 2.7.2, Fedora release 16 (Verne)
#               KWrite 4.8.1, python 2.7.2, Fedora release 16 (Verne)
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
_FILTER_OPT_VAR = "filt_file_name"
# variable to receive the ID column
_ID_COL_OPT_VAR = "id_column"
# variable to receive the output layout
_LAYOUT_OPT_VAR = "layout"
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
    parser = optparse.OptionParser("%prog [OPTION...] RECORDFILE",
        formatter=optparse.TitledHelpFormatter(width=78),
        add_help_option=None)

    # define options here:
    parser.add_option(      # ID filter file
        '-f', '--filter', dest=_FILTER_OPT_VAR,
        help="Use this file to filter records by ID's.")
    parser.add_option(      # ID column
        '-i', '--id-column', dest=_ID_COL_OPT_VAR, type="int", default=0,
        help="Read the record ID from this column.")
    parser.add_option(      # output layout
        '-l', '--layout', dest=_LAYOUT_OPT_VAR,
        help="Use this comma-separated list of column numbers to format the "
        "output.")
    parser.add_option(      # filtered record output file
        '-o', '--output', dest=_OUT_OPT_VAR,
        help='Save the filtered records into this file.')
    parser.add_option(      # customized description; put --help last
        '-h', '--help', action='help',
        help='Show this help message and exit.')

    settings, args = parser.parse_args(argv)

    # check number of arguments:
    mandatory_args = 1
    extra_args = len(args) - mandatory_args

    if extra_args:
        parser.error('program takes exactly one record file; '
                     '{}.'.format(
                     '"{}" ignored'.format(args[mandatory_args:]) if
                     extra_args > 0 else "none specified"))

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
    rec_rd_permit = "rb"
    rec_map = {}
    with open(rec_file, rec_rd_permit) as rec_list_file:

        rec_reader = csv.reader(rec_list_file)
        id_col = getattr(settings, _ID_COL_OPT_VAR)

        for rec in rec_reader:
            if rec:

                rec_map[rec[id_col]] = rec
                debug("Found record %s: %s", rec[id_col], rec)

            else:
                debug("Empty line encountered!")

    filter_file = getattr(settings, _FILTER_OPT_VAR)
    info("Finished reading record file %s, generating filtered list "
        "from ID filter file %s...", rec_file, filter_file)
    # Extract filtered records.
    out_file = getattr(settings, _OUT_OPT_VAR)
    wrt_permit = 'w'
    res_file = open(out_file, wrt_permit) if out_file else sys.stdout
    out_rec_file = csv.writer(res_file)
    with open(filter_file) as filter_list:

        out_layout = getattr(settings, _LAYOUT_OPT_VAR)

        if out_layout:

            col_sep = ','
            out_layout = \
                map(lambda col_str: int(col_str), out_layout.split(col_sep))
            debug("output layout: %s", out_layout)

        for id in filter_list:

            id = id.splitlines()[0]

            if id in rec_map:

                # Format the output columns as specified if a custom
                # format was provided.  Since records may have different
                # lengths, indices beyond the length of short records
                # may be simply dropped.
                fields = rec_map[id]

                if out_layout:

                    rec_layout = filter(
                        lambda col_num: col_num < len(rec_map[id]), out_layout)
                    debug("custom output layout for record %s: %s", id,
                        rec_layout)
                    fields = \
                        map(lambda col_num: rec_map[id][col_num], rec_layout)

                out_rec_file.writerow(fields)

            else:
                logging.warn("Unknown record %s encountered, skipping...", id)

    if out_file:
        res_file.close()

    info("Done!")


if __name__ == '__main__':
    status = main()
    sys.exit(status)
