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
import numpy as np
from twissfit.twiss import *
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
        nfiles = len(files)
        nfiles_min = 3
        ntries = 4
        if nfiles < nfiles_min:
            print('Please provide at least {} files.'.format(nfiles_min))
            sys.exit()
        result_matrix = np.array([], dtype=np.float64)
        for file in files:
            for i in reversed(range(ntries)):
                try:
                    # make sure the user input values are all positive
                    k_prime_l_quad = np.abs(float(
                        input("Please enter the K'L for {}: ".format(file))))
                    # print(k_prime_l_quad)
                    grid_data = ProfileGridData(file)
                    sigma_x, sigma_y = grid_data.process_horiz_and_vert(
                        verbose=False)
                    result_matrix = np.append(
                        result_matrix, (k_prime_l_quad, sigma_x, sigma_y))
                except (KeyboardInterrupt, EOFError) as e:
                    print('\nNothing to do.')
                    sys.exit()
                except ValueError as e:
                    if i == 0:
                        print('Too many wrong entries.\nNothing to do.\n')
                        sys.exit()
                    print(
                        '\nNot a valid number. Please try again. You have {} tries left.'.format(i))
                    continue
                break
        result_matrix = result_matrix.reshape((nfiles, 3))
        beta_x, alpha_x, eps_x, beta_y, alpha_y, eps_y = solve_equation_system(
            result_matrix)
        plot_sigma_vs_distance(result_matrix, beta_x,
                               alpha_x, eps_x, beta_y, alpha_y, eps_y)
        plot_sigma_vs_k_prime_l(result_matrix, beta_x,
                                alpha_x, eps_x, beta_y, alpha_y, eps_y)
        sys.exit()

    print('\nNothing to do.')


if __name__ == "__main__":
    main()
