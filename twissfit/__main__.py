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
import logging as log
import numpy as np
from PyPDF2 import PdfFileMerger
from twissfit.twiss import *
from twissfit.version import __version__
from twissfit.profilegriddata import ProfileGridData


def main():
    scriptname = 'twissfit'
    contains = False
    parser = argparse.ArgumentParser()
    parser.add_argument('--version',
                        help='Print version', action='store_true')
    parser.add_argument(
        '-v', '--verbose', help='Increase output verbosity', action='store_true')
    parser.add_argument('-s', '--sim', nargs=1, type=int,
                        help='Number of simulated data files to produce.')
    parser.add_argument('-p', '--process', nargs='*', type=str,
                        help='Process files.')
    parser.add_argument('-c', '--contains', action="store_true", default=False,
                        help="File name contains the K'L value.")

    args = parser.parse_args()
    if args.verbose:
        log.basicConfig(level=log.INFO)
        pass

    if args.version:
        print('{} {}'.format(scriptname, __version__))
        sys.exit()

    if args.contains:
        contains = True

    if args.sim:
        nsim = int(args.sim[0])
        log.info('Creating {} simulated data files.'.format(nsim))
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
            log.error(
                'Please provide at least {} files.'.format(nfiles_min))
            sys.exit()
        result_matrix = np.array([], dtype=np.float64)

        if contains:
            for file in files:
                try:
                    k_prime_l_quad = float(file[:4])
                except:
                    log.error(
                        'When using the -c switch, the first 4 digits of the file name must contain a valid float. Aborting.')
                    sys.exit()
                grid_data = ProfileGridData(file)
                sigma_x, sigma_y, plot_filename_hor, plot_filename_vert = grid_data.process_horiz_and_vert()
                result_matrix = np.append(
                    result_matrix, (k_prime_l_quad, sigma_x, sigma_y))
                plot_filenames.extend(
                    [plot_filename_hor, plot_filename_vert])
                # sys.exit()

        else:

            for file in files:
                for i in reversed(range(ntries)):

                    try:
                        # make sure the user input values are all positive
                        k_prime_l_quad = np.abs(float(
                            input("Please enter the K'L for {}: ".format(file))))
                        grid_data = ProfileGridData(file)
                        sigma_x, sigma_y, plot_filename_hor, plot_filename_vert = grid_data.process_horiz_and_vert(
                            verbose=False)
                        result_matrix = np.append(
                            result_matrix, (k_prime_l_quad, sigma_x, sigma_y))
                        plot_filenames.extend(
                            [plot_filename_hor, plot_filename_vert])

                    except (KeyboardInterrupt, EOFError) as e:
                        log.error('\nNothing to do.')
                        sys.exit()

                    except ValueError as e:
                        if i == 0:
                            log.error(
                                'Too many wrong entries. Nothing to do.')
                            sys.exit()
                        log.error(
                            'Not a valid number. Please try again. You have {} tries left.'.format(i))
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

    log.error('Nothing to do.')


if __name__ == "__main__":
    main()
