# twissfit

## Introduction

This is an accelerator physics calculator. It is used for fitting measured data on a profile grid monitor which is further away downstream from a quadupole magnet, in order to optimize the quadrupole strength. It an be used with any beam line, but the specific beam line in question was the FRS at GSI facility.

Most calculations are based on the following reference [H. Wollnik, Optics of Charged Particles, Academic Press, 1987](http://www.worldcat.org/oclc/471604996), formulas on pages 52, 152 and 154. In the above reference, B, A and C are beta, alpha and gamma Twiss / Courant-Snyder parameters.

## Working principle

First the transformation matrix of the system of quadupole with its fringing fields and a drift space is calculated. Then the Twiss matrix is determined.

Using 3 or more values set for quadupole strength manually, the width of the beam is measured at the profile grid. From these three values are a linear equation system (determined for 3 variables, but over-determined for more) is constructed each with the first line of the Twiss matrix. The resulting solutions are then **beta*eps**, **alpha*eps** and **gamma*eps**. Then, epsilon is then calculated, and with that the values of **alpha**, **beta** and **gamma** at the quadrupole entry. These information can be used to now create plots while varying either distance or quadrupole strength in order to find the position of the minima manually.

## Installation

Installation requires the following libraries to run: **numpy**, **scipy**, **matplotlib** and **pypdf2**, which can be installed by using `pip`:

    pip install numpy scipy matplotlib pypdf2

To run locally without installation:

    python3 -m twissfit

You can also install the package using setup tools.

    python3 setup.py install --record installed_files.txt

The files that are installed to your computer will be listed in the installed_files.txt so  that you can remove them at a later time if you like to remove the module. You can list the files by using:

    xargs ls -la < installed_files.txt

or delete them (be careful!) using:

    xargs rm -rf < installed_files.txt

## Usage

In general the `-v` or the `--verbose` switch increases the verbosity in all operations.

In order to test the code, you can create test datasets. To create 3 simulated data sets you can use:

    python3 -m twissfit -s 3

Whether you have simulated data or real data from the detector, you would like to either have a plot and check them, or you like to process them completely. If you just like to draw the fits and have a look at them, you can use the `-d` option, like:

    python -m twissfit -d *.csv

This creates the corresponding plots with the fits. You can use this option to get the initial feeling for your raw data before you further process them.

Finally in order to process the files completely them you may:

    python3 -m twissfit -p *.csv

The resulting PDFs are stored in one single file, using the name of the first file in the series.

You can provide the `-c` switch to tell the script that the file names already contain the K'L values so the script will not ask you anymore.

    python3 -m twissfit -c -p *.csv

This works only if the first 4 characters of the file name contain the value, like:

    0.60_71d6e49e-0794-11ea-a666-4a0003a87d10.csv

which means the value of K'L for this file is 0.6.

A configuration file can be provided with the `-p` flag to the command line. This config file should be in JSON format, i.e. a ASCII file, which you can for example call `init_params.json` with the following content:

- x_omit: List of malfunctioning channels in horizontal detector
- y_omit: List of malfunctioning channels in vertical detector
- fit_params: list of starting values for the fit parameters
- variant: determines what type of data the detectors deliver, 47 point variant, 77 point variant and 96 point variant


    {
        'x_omit': [...],    
        'y_omit': [...],
        'fit_params': [...],
        'varaint' : ...,
    }


for example, like:


    {
        'x_omit': [-20, -19, -18, -17],    
        'y_omit': [],
        'x_fit_params': [offset, slope, amp, mean, sigma, cut_range],
        'y_fit_params': [offset, slope, amp, mean, sigma, cut_range],
        'variant' : 47,
    }


which means, that 4 channels are ignored in the data from the horizontal detector, and no channels from the vertical detector. Some corresponding values are set instead of offset, slope, etc... and the last point demonstrate that we have a 47 point variant of data from the profile grid detector. Default values are `[None, None, None, None, None, None]`, which means the script tries to estimate by itself. In any case you can provide mixed values and/or `None` also in the JSON init file.

In the above examples, the usage of the JSON initialiser would look like the following:

    python -m twissfit -i init_file.json -d *.csv

or

    python3 -m twissfit -c -i init_file.json -p *.csv



## Gallery

<img src="https://raw.githubusercontent.com/xaratustrah/twissfit/master/beamline.jpg" width="">
<img src="https://raw.githubusercontent.com/xaratustrah/twissfit/master/screenshot.png" width="">
