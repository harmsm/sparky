#!/usr/bin/env python
__description__ = \
"""
sparky_delete-peaks.py 

Delete peaks in Sparky .save files using peaks in input file input file.  
"""

__author__ = "Michael J. Harms"
__date__ = "080409"
__usage__ = "sparky_delete-peaks.py input-file $1.save $2.save ... $n.save"

import os, sys

class SparkyDeletePeaksError(Exception):
    """
    General error class for this module.
    """

    pass

def readPeakList(peak_file):
    """
    Read in list of peaks to delete from peaks_file.  Comment lines (#) and
    blank lines are ignored.
    """ 

    f = open(peak_file,'r')
    peak_list = f.readlines()
    f.close()
   
    peak_list = [l for l in peak_list if l[0] != "#" and l.strip() != ""] 
    peak_list = [l.strip() for l in peak_list]   
 
    return peak_list

def convertSparkyFile(sparky_file,peak_list):
    """
    Delete peaks in sparky_file using peak_list. 
    """

    f = open(sparky_file,'r')
    sparky = f.readlines()
    f.close()

    keep_lines = [True for l in sparky]
    peak_lines = [i for i, l in enumerate(sparky) if l[0:9] == "type peak"]
    end_ornament = [i for i, l in enumerate(sparky)
                    if l[0:14] == "<end ornament>"]
    peak_lines.append(end_ornament[0])

    peak_lines = [(peak_lines[i-1],peak_lines[i])
                  for i in range(1,len(peak_lines))]

    # Use rs lines to find peaks to delete
    for p in peak_lines:

        peak = sparky[p[0]:p[1]]        
        
        hash = [l[0:3] for l in peak]
        rs = peak[hash.index("rs ")]
        column = rs[4:].split("|")
        if column[0] in peak_list or column[3] in peak_list:
            for i in range(p[0],p[1]):
                keep_lines[i] = False    
 
    # Create output file, taking only lines with keep_lines == True
    out = [l for i, l in enumerate(sparky) if keep_lines[i]]

    # Write output
    g = open(sparky_file,'w')
    g.writelines(out)
    g.close()


def main():
    """
    If called from command line...
    """

    # Parse command line
    try:
        peak_file = sys.argv[1]
        sparky_files = sys.argv[2:]
    except IndexError:
        print __usage__
        sys.exit()

    # Read in peak conversion rules
    peak_list = readPeakList(peak_file)
   
    # Make sure that sparky files exist 
    file_check = [os.path.isfile(f) for f in sparky_files]
    if False in file_check:
        print "Not all specified sparky save files exist!"
        sys.exit()
   
    sparky_files.sort() 
    for sparky_file in sparky_files:
        print sparky_file
        convertSparkyFile(sparky_file,peak_list)    
        


if __name__ == "__main__":
    main()
