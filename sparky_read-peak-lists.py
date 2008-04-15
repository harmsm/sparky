#!/usr/bin/env python
__description__ = \
"""
sparky_read-peak-lists.py

Reads a set of sparky peak lists, parsing filename to extract experiment pH.
"""
__author__ = "Michael J. Harms"
__date__ = "080415"
__usage__ = "sparky_read-peak-lists.py dir_with_list_files"

import os, sys

class SparkyReadPeakListsError(Exception):
    """
    General error class for this module.
    """

    pass

def readPeakFile(peak_file):
    """
    Read the contents of a peak file (assignment, w1, and w2).
    """

    print peak_file

    f = open(peak_file,'r')
    peaks = f.readlines()
    f.close()

    # Remove header, comments, and blank lines
    peaks = [l for l in peaks[1:] if l[0] != "#" and l.strip() != ""]
    peaks = [(l.split()[0],(float(l.split()[1]),float(l.split()[2])))
             for l in peaks]

    return dict(peaks)

def processPeakFiles(file_list):
    """
    Take set of files, extract peaks, sort by pH, then generate R-readable
    output.
    """

    pH_values = [l.split("_")[1] for l in file_list]
    pH_values = [float("%s.%s" % tuple(p.split("p"))) for p in pH_values]

    # Extract data, keyed to pH
    all_data = zip(pH_values,file_list)
    all_data = dict([(f[0],readPeakFile(f[1])) for f in all_data])

    # Grab unique assignments  
    all_peak_labels = [all_data[p].keys() for p in pH_values]
    flattened_labels = []
    for peak_list in all_peak_labels:
        flattened_labels.extend(peak_list)
    unique_labels = dict([(l,0) for l in flattened_labels]).keys()
  
    unique_labels.sort()  
    pH_values.sort()

    i = 0
    out = ["# Taken from data in:\n"]
    out.extend(["#   %s\n" % f for f in file_list])
    out.append("%10s%15s%10s%10s%10s\n" % ("  ","peak","pH","w1","w2"))
    for peak in unique_labels:
        for pH in pH_values:
            try:
                out.append("%10i%15s%10.3F%s\n" % \
                           (i,peak,pH,"%10.3F%10.3F" % all_data[pH][peak]))
            except KeyError:
                out.append("%10i%15s%10.3F%10s%10s\n" % (i,peak,pH,"NA","NA"))

            i += 1
    
    return "".join(out)    



def main():
    """
    Function called if run from command line.
    """

    try:
        inp_dir = sys.argv[1]
    except IndexError:
        print __usage__
        sys.exit()    

    try:   
        file_list = os.listdir(inp_dir)
        os.chdir(inp_dir)
        file_list = [f for f in file_list if f[-5:] == ".list"]
        file_list.sort()
        if len(file_list) == 0:
            raise OSError
    except OSError:
        err = "%s is either not a directory or contains no .list files!"
        raise SparkyReadPeakListsError(err)

    
    out = processPeakFiles(file_list)
    print out,

if __name__ == "__main__":
    main()
