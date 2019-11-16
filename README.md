# twissfit

## Introduction

This is an accelerator physics calculator. It is used for fitting measured data on a profile grid monitor which is further away downstream from a quadupole magnet, in order to optimize the quadrupole strength. It an be used with any beam line, but the specific beam line in question was the FRS at GSI facility.

Most calculations are based on the following reference [H. Wollnik, Optics of Charged Particles, Academic Press, 1987](http://www.worldcat.org/oclc/471604996), formulas on pages 52, 152 and 154. In the above reference, B, A and C are beta, alpha and gamma Twiss / Courant-Snyder parameters.

## Working principle

First the transformation matrix of the system of quadupole with its fringing fields and a drift space is calculated. Then the Twiss matrix is determined.

Using 3 or more values set for quadupole strength manually, the width of the beam is measured at the profile grid. From these three values are a linear equation system (determined for 3 variables, but over-determined for more) is constructed each with the first line of the Twiss matrix. The resulting solutions are then **beta*eps**, **alpha*eps** and **gamma*eps**. Then, epsilon is then calculated, and with that the values of **alpha**, **beta** and **gamma** at the quadrupole entry. These information can be used to now create plots while varying either distance or quadrupole strength in order to find the position of the minima manually.

## Installation

To run locally without installation:

    python3 -m twissfit

You can also install the package using setup tools.

    python3 setup.py install --record installed_files.txt

The files that are installed to your computer will be listed in the installed_files.txt so  that you can remove them at a later time if you like to remove the module. You can list the files by using:

    xargs ls -la < installed_files.txt

or delete them (be careful!) usin:

    xargs rm -rf < installed_files.txt

## Usage

To create 3 simulated data sets you can use:

    python3 -m twissfit -s 3

Finally in order to process them you may:

    python3 -m twissfit -p *.csv


## Gallery

<img src="https://raw.githubusercontent.com/xaratustrah/twissfit/master/screenshot.png" width="">
