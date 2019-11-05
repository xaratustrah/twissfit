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
from twissfit.version import __version__
from twissfit.profilegriddata import ProfileGridData


def main():
    for file in sys.argv[1:]:
        grid_data = ProfileGridData(file)
        grid_data.process_horiz_and_vert()


if __name__ == "__main__":
    main()
