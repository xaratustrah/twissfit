# -*- coding: utf-8 -*-
"""
Profile grid data interface
Exporter, Fitter, plotter

2019

Xaratustrah (S. Sanjari)

"""
import os
import uuid
import numpy as np
from scipy.optimize import curve_fit
import sys
import logging as log
from io import BytesIO
import matplotlib.pyplot as plt


class ProfileGridData(object):
    def __init__(self, filename, init_dict):
        self.filename = filename
        self.filename_base = os.path.basename(filename)
        self.filename_wo_ext = os.path.splitext(filename)[0]
        self.x_data = np.array([])
        self.y_data = np.array([])
        self.init_dict = init_dict

    def _read_data(self):
        # 47 point variant
        if self.init_dict['variant'] == 47:
            xvals = np.genfromtxt(self.filename, delimiter=',',
                                  skip_header=5, skip_footer=62)
            yvals = np.genfromtxt(self.filename, delimiter=',', skip_header=67)

        # 77 point variant
        if self.init_dict['variant'] == 77:
            xvals = np.genfromtxt(self.filename, delimiter=',',
                                  skip_header=5, skip_footer=78)
            yvals = np.genfromtxt(self.filename, delimiter=',', skip_header=83)

        # 96 point varaint
        if self.init_dict['variant'] == 96:
            xvals = np.genfromtxt(self.filename, delimiter=',',
                                  skip_header=5, skip_footer=1)
            yvals = np.zeros((95, 2))

        self.x_data = xvals
        self.y_data = yvals
        self.xy_data = np.concatenate((xvals, yvals), axis=1)
        self.xy_data = np.delete(self.xy_data, 2, 1)
        log.info('Data point length before omit: {}'.format(
            np.shape(self.xy_data)[0]))

        # omit the malfunctioning rows from the x_data
        rowcnt = 0
        rowdellist = []
        for row in self.x_data:
            if row[0] in self.init_dict['x_omit']:
                rowdellist.append(rowcnt)
            rowcnt += 1
        self.x_data = np.delete(self.x_data, rowdellist, axis=0)
        log.info('Data point length after x_omit: {}'.format(
            np.shape(self.x_data)[0]))

        # omit the malfunctioning rows from the x_data
        rowcnt = 0
        rowdellist = []
        for row in self.y_data:
            if row[0] in self.init_dict['y_omit']:
                rowdellist.append(rowcnt)
            rowcnt += 1
        self.y_data = np.delete(self.y_data, rowdellist, axis=0)
        log.info('Data point length after y_omit: {}'.format(
            np.shape(self.y_data)[0]))

    @staticmethod
    def create_sim_data():
        x = np.arange(-45, 46.5, 1.5)
        amp = np.random.randint(800, 1800)
        mu = np.random.randint(-20, 20)
        sigma = np.random.randint(2, 10)
        popt = [0, 0, amp, mu, sigma]
        vals = ProfileGridData.fit_function(x, *popt)
        plt.plot(x, vals, 'ro', label='Fit')
        # np.vstack((x, vals)).T
        return x, vals, amp, mu, sigma

    @staticmethod
    def write_sim_data():
        filename = str(uuid.uuid1()) + '.csv'
        xh, valsh, amph, muh, sigmah = ProfileGridData.create_sim_data()
        xv, valsv, ampv, muv, sigmav = ProfileGridData.create_sim_data()
        with open(filename, 'w') as file:
            file.write('device:\nSIMULATION\ngain:\nSIMULATION\n')
            file.write(
                'x-values: (Amp {} Mu {} Sigma {})\n'.format(amph, muh, sigmah))
            for i in range(len(xh)):
                file.write('{}, {}\n'.format(xh[i], valsh[i]))
            file.write(
                'y-values: (Amp {} Mu {} Sigma {})\n'.format(ampv, muv, sigmav))
            for i in range(len(xv)):
                file.write('{}, {}\n'.format(xv[i], valsv[i]))

    @staticmethod
    def fit_function(x, *p):
        """
        Line + 1 Gaussian
        """
        return p[0] + p[1] * x + p[2] * np.exp(-(x - p[3]) ** 2 / (2. * p[4] ** 2))

    @staticmethod
    def fit_and_plot(x_data, y_data, fit_params, title='', filename=''):

        # x and y are the variables for the fitter
        x = x_data
        x_for_plotting = np.linspace(x_data.min(), x_data.max(), 400)
        y = y_data

        # take values from init JSON or estimate default values
        # params are like: [offset, slope, amp, mean, sigma, cut_range]

        mean_idx = y.argmax()

        if not fit_params[0]:
            offset = y[mean_idx - 5]
        else:
            offset = fit_params[0]

        if not fit_params[1]:
            slope = 1
        else:
            slope = fit_params[1]

        if not fit_params[2]:
            amp = 1000
        else:
            amp = fit_params[2]

        if not fit_params[3]:
            mean = x[mean_idx]
        else:
            mean = fit_params[3]

        if not fit_params[4]:
            sigma = 20
        else:
            sigma = fit_params[4]

        if not fit_params[5]:
            cut_range = 2 * sigma
        else:
            cut_range = fit_params[5]

        p = [offset, slope, amp, mean, sigma]
        # defining the fitting region
        data_cut = (x > mean - cut_range) & (x < mean + cut_range)
        x_for_plotting_data_cut = (
            x_for_plotting > mean - cut_range) & (x_for_plotting < mean + cut_range)

        # fit
        popt, pcov = curve_fit(ProfileGridData.fit_function,
                               x[data_cut], y[data_cut], p0=p)
        mean = popt[3]
        sigma = np.abs(popt[4])  # make sure sigma is positive

        area = sum(ProfileGridData.fit_function(x, *popt))
        # plot with original data
        fig = plt.figure()
        ax = fig.gca()
        ax.plot(x, y, 'kx', label='Data')
        ax.plot(x_for_plotting[x_for_plotting_data_cut], ProfileGridData.fit_function(
            x_for_plotting[x_for_plotting_data_cut], *popt), 'r', label='Fit')
        ax.set_xlabel('mean = {:0.2e}, sigma = {:0.2e}, area = {:0.2e}'.format(
            mean, sigma, area))
        ax.set_title(title)

        # Now add the legend with some customizations.
        legend = ax.legend(loc='upper right', shadow=False)

        # Set legend fontsize
        for label in legend.get_texts():
            label.set_fontsize('small')

        plt.grid()
        if filename:
            plt.savefig(filename)
        return popt, area

    def process_horiz_and_vert(self, verbose=False):
        self._read_data()

        # horizontal direction
        x_pos = self.x_data[:, 0]
        hor_grid = self.x_data[:, 1]
        plot_filename_hor = '{}_Horizontal.pdf'.format(self.filename_wo_ext)
        popt, area = ProfileGridData.fit_and_plot(
            x_pos, hor_grid, self.init_dict['x_fit_params'], title='{}_Horizontal'.format(self.filename_base), filename=plot_filename_hor)
        log.info('File Name | Offset | Slope | Amplitude | Mean | Sigma')
        log.info('{} | {} | {}'.format(self.filename_base,
                                       ' | '.join(map(str, popt)), area))
        mean_x = popt[3]
        sigma_x = np.abs(popt[4])  # make sure sigma is positive

        # vertical direction
        y_pos = self.y_data[:, 0]
        ver_grid = self.y_data[:, 1]
        plot_filename_vert = '{}_Vertical.pdf'.format(self.filename_wo_ext)
        popt, area = ProfileGridData.fit_and_plot(
            y_pos, ver_grid, self.init_dict['y_fit_params'], title='{}_Vertical'.format(self.filename_base), filename=plot_filename_vert)
        log.info('File Name | Offset | Slope | Amplitude | Mean | Sigma')
        log.info('{} | {} | {}'.format(self.filename_base,
                                       ' | '.join(map(str, popt)), area))
        mean_y = popt[3]
        sigma_y = np.abs(popt[4])  # make sure sigma is positive
        return mean_x, mean_y, sigma_x, sigma_y, plot_filename_hor, plot_filename_vert
