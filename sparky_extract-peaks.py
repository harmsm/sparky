#!/usr/bin/env python
__description__ = \
"""
sparky_extract-peaks.py 

Extract all peaks in all sparky .save files in a directory, writing to an 
R-readable list.  This program assumes that the pH of each experiment is in the
filename with style: pH_7p01_*.save.  
"""

__author__ = "Michael J. Harms"
__date__ = "080410"
__usage__ = "sparky_extract-peaks.py"

import os, sys


def extractPeaks(sparky_file):
    """
    Extract peaks from sparky_file.
    """

    f = open(sparky_file,'r')
    sparky = f.readlines()
    f.close()

    # Create peak_lines, a list of tuples that describe the line-numbers of 
    # each peak.
    peak_lines = [i for i, l in enumerate(sparky) if l[0:9] == "type peak"]
    end_ornament = [i for i, l in enumerate(sparky)
                    if l[0:14] == "<end ornament>"]
    peak_lines.append(end_ornament[0])
    peak_lines = [(peak_lines[i-1],peak_lines[i])
                  for i in range(1,len(peak_lines))]

    peak_list = []
    for p in peak_lines:

        peak = sparky[p[0]:p[1]]        
        hash = [l[0:3] for l in peak]

        # Peak label. This try/except statement will skip all unlabeled peaks.
        try:
            rs = peak[hash.index("rs ")][4:].split("|")
            aa_type = "%10s" % rs[0][0:3]
            res_num = "%10i" % int(rs[0][3:])
            atoms = "%10s" % ("%s-%s" % (rs[1],rs[4]))
        except ValueError:
            continue
       
        # Peak position 
        pos = peak[hash.index("pos")][4:].split()
        w1 = "%10.3F" % float(pos[0])
        w2 = "%10.3F" % float(pos[1])
       
        # Peak height 
        height = peak[hash.index("hei")][7:].split()
        height = "%10.2E" % float(height[1])

        # Peak integral
        try:
            integral = peak[hash.index("int")][9:].split()
            integral = "%10.2E" % float(integral[0])
        except ValueError:
            integral = "%10s" % "NA"
        
        # Peak note
        try:
            note = peak[hash.index("not")][5:].strip()
            note = note[1:-1]   # remove trailing quotes
            note = "%30s" % ("\"%s\"" % (note[:26]))
        except ValueError:
            note = "%30s" % "NA"

        peak_list.append((3*"%s" % (res_num,aa_type,atoms),
                          5*"%s" % (w1,w2,height,integral,note)))

    return dict(peak_list)



def main():
    """
    If called from command line...
    """

    # Create list of sparky files
    sparky_files = os.listdir('.')
    sparky_files = [f for f in sparky_files if f[-5:] == ".save"]

    # Create list of pH values
    pH_values = [l.split("_")[1] for l in sparky_files]
    pH_values = [float("%s.%s" % tuple(p.split("p"))) for p in pH_values]

    # Extract peaks from each file at each pH
    all_peaks = dict([(pH_values[i],extractPeaks(f))
                      for i, f in enumerate(sparky_files)])

    # Create list of unique peaks, sorted by residue number
    all_peak_labels = [pH.keys() for pH in all_peaks.values()]
    flattened_labels = []
    for peak_list in all_peak_labels:
        flattened_labels.extend(peak_list)
    unique_labels = dict([(l,0) for l in flattened_labels]).keys()
    to_sort = [(int(l.split()[0]),l) for l in unique_labels]
    to_sort.sort()
    peak_labels = [l[1] for l in to_sort]


    # Write output in R-readable format
    i = 0
    output = ["%10s%10s%10s%10s%10s%10s%10s%10s%10s%30s\n" % \
           (" ","residue","aa","atoms","pH","w1","w2","height","volume","note")]
    pH_values.sort()
    for peak in peak_labels:
        for pH in pH_values:
            try:
                peak_data = all_peaks[pH][peak]
                output.append("%10i%s%10.3F%s\n" % (i,peak,pH,peak_data))
            except KeyError:
                output.append("%10i%s%10.3F%10s%10s%10s%10s%30s\n" % \
                              (i,peak,pH,"NA","NA","NA","NA","NA"))
            i += 1

    print "".join(output)
   
 


if __name__ == "__main__":
    main()
