#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Profile grid data and twiss parameter fitter
Exporter, Fitter, plotter

2019

Xaratustrah (S. Sanjari)

"""
import os
import sys
import argparse
import numpy as np
from PyPDF2 import PdfFileMerger
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
        plot_filenames = []
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
                    sigma_x, sigma_y, plot_filename_hor, plot_filename_vert = grid_data.process_horiz_and_vert(
                        verbose=False)
                    result_matrix = np.append(
                        result_matrix, (k_prime_l_quad, sigma_x, sigma_y))
                    plot_filenames.extend(
                        [plot_filename_hor, plot_filename_vert])

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
        plt_file_1 = plot_sigma_vs_distance(result_matrix, beta_x,
                                            alpha_x, eps_x, beta_y, alpha_y, eps_y)
        plt_file_2 = plot_sigma_vs_k_prime_l(result_matrix, beta_x,
                                             alpha_x, eps_x, beta_y, alpha_y, eps_y)
        plot_filenames.insert(0, plt_file_1)
        plot_filenames.insert(0, plt_file_2)
        # merge PDFs
        merger = PdfFileMerger()
        for pdf in plot_filenames:
            merger.append(pdf)
            os.remove(pdf)  # delete the file!
        merger.write('{}_all.pdf'.format(
            os.path.splitext(plot_filenames[2])[0]))
        merger.close()
        sys.exit()

    print('\nNothing to do.')


if __name__ == "__main__":
    main()
