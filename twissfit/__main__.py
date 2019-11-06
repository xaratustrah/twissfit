#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Profile grid data and twiss parameter fitter
Exporter, Fitter, plotter

2019

Xaratustrah

"""
import os
import sys
import argparse
from twissfit.version import __version__
from twissfit.profilegriddata import ProfileGridData


def main():
    scriptname = 'twissfit'
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version',
                        help='Print version', action='store_true')
    parser.add_argument('-s', '--sim', nargs=1, type=int,
                        help='Number of simulated data files to produce.')
    parser.add_argument('-p', '--process', nargs='*', type=str,
                        help='Process files.')

    args = parser.parse_args()
    if args.version:
        print('{} {}'.format(scriptname, __version__))
        sys.exit()

    if args.sim:
        nsim = int(args.sim[0])
        print('Creating {} simulated data files.'.format(nsim))
        for i in range(nsim):
            ProfileGridData.write_sim_data()
        sys.exit()

    if args.process:
        files = args.process
        for file in files:
            grid_data = ProfileGridData(file)
            grid_data.process_horiz_and_vert()
        sys.exit()

    print('Nothing to do.')


if __name__ == "__main__":
    main()
