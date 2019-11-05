# -*- coding: utf-8 -*-
"""
Profile grid data and twiss parameter fitter
Exporter, Fitter, plotter

2019

Xaratustrah

"""
import os
import numpy as np
from scipy.optimize import curve_fit
import sys
from io import BytesIO
import matplotlib.pyplot as plt

RANGE = 30
SIGMA_ESTIMATE = 20


class ProfileGridData(object):
    def __init__(self, filename):
        self.filename = filename
        self.filename_base = os.path.basename(filename)
        self.filename_wo_ext = os.path.splitext(filename)[0]
        self.data = np.array([])

    def _read_data(self):
        xvals = np.genfromtxt(self.filename, delimiter=',',
                              skip_header=5, skip_footer=62)
        yvals = np.genfromtxt(self.filename, delimiter=',', skip_header=67)
        self.data = np.concatenate((xvals, yvals), axis=1)
        self.data = np.delete(self.data, 2, 1)

    @staticmethod
    def fit_function(x, *p):
        """
        Line + 1 Gaussian
        """
        return p[0] + p[1] * x + p[2] * np.exp(-(x - p[3]) ** 2 / (2. * p[4] ** 2))

    @staticmethod
    def fit_and_plot(x_data, y_data, name=""):

        y = y_data
        #x = x_data
        #pos = x_data
        x = np.arange(len(y))

        # Estimate for mean and sigma
        mean = y.argmax()
        sigma = SIGMA_ESTIMATE
        offset = y[mean - 5]
        slope = 1
        amp = 1
        p = [offset, slope, amp, mean, sigma]
        # defining the fitting region
        data_cut = (x > mean - RANGE) & (x < mean + RANGE)

        # fit
        popt, pcov = curve_fit(ProfileGridData.fit_function,
                               x[data_cut], y[data_cut], p0=p)

        # Get the area
        area = sum(ProfileGridData.fit_function(x, *popt))
        print(popt)
        # plot with original data
        fig = plt.figure()
        ax = fig.gca()
        ax.plot(x, y, 'kx', label='Data')
        ax.plot(x[data_cut], ProfileGridData.fit_function(
            x[data_cut], *popt), 'r', label='Fit')
        ax.set_xlabel('mu = {:0.2e}, sig = {:0.2e}, area = {:0.2e}'.format(
            popt[3], popt[4], area))
        ax.set_title(name)

        # Now add the legend with some customizations.
        legend = ax.legend(loc='upper right', shadow=False)

        # Set legend fontsize
        for label in legend.get_texts():
            label.set_fontsize('small')

        plt.grid()
        plt.savefig('{}.pdf'.format(name))
        print(name, ' '.join(map(str, popt)), area)

    def process_horiz_and_vert(self):
        self._read_data()
        pos = self.data[:, 0]
        hor_grid = self.data[:, 1]
        ver_grid = self.data[:, 2]
        ProfileGridData.fit_and_plot(
            pos, hor_grid, name='{}_Horizontal'.format(self.filename_base))
        ProfileGridData.fit_and_plot(
            pos, ver_grid, name='{}_Vertical'.format(self.filename_base))
