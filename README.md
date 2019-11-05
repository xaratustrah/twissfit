# twissfit
Fit data from a profile grid monitor and calculate TWISS parameters for the quadrupole behind it.

To run locally without installation:

    python3 -m twissfit

You can also install the package using setup tools.

    python3 setup.py install --record installed_files.txt

The files that are installed to your computer will be listed in the installed_files.txt so  that you can remove them at a later time if you like to remove the module. You can list the files by using:

    xargs ls -la < installed_files.txt

or delete them (be careful!) usin:

    xargs rm -rf < installed_files.txt
