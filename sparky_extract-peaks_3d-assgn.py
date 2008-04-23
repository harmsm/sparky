#!/usr/bin/env python
__description__ = \
"""
sparky_extract-peaks_3d-assgn.py 

"""

__author__ = "Michael J. Harms"
__date__ = "080410"
__usage__ = "sparky_extract-peaks.py dir_with_save_files"

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
            aa_type = "%10s" % rs[3][0:3]
            res_num = "%10i" % int(rs[3][3:])
            atoms = "%10s" % rs[4]
            assgn_atoms = "%28s" % ("%s-%s,%s-%s" % (rs[0],rs[1],rs[6],rs[7]))
        except ValueError:
            continue
       
        # Peak position 
        pos = peak[hash.index("pos")][4:].split()
        w1 = "%10.3F" % float(pos[0])
        w2 = "%10.3F" % float(pos[1])
        w3 = "%10.3F" % float(pos[2])
 
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

        peak_list.append((4*"%s" % (res_num,aa_type,atoms,assgn_atoms),
                          6*"%s" % (w1,w2,w3,height,integral,note)))

    return dict(peak_list)



def main():
    """
    If called from command line...
    """

    try:
        sparky_file = sys.argv[1]
    except IndexError:
        print __usage__
        sys.exit()


    peaks = extractPeaks(sparky_file)
 
    to_sort = [(int(l.split()[0]),l) for l in peaks.keys()]
    to_sort.sort()
    peak_labels = [l[1] for l in to_sort]
    
    # Write output in R-readable format
    i = 0
    output = ["# Taken from %s\n" % os.path.abspath(sparky_file)]
    output.append("%10s%10s%10s%10s%28s%10s%10s%10s%10s%10s%30s\n" % \
           (" ","residue","aa","atoms","assgn_atoms","w1","w2","w3","height",
            "volume","note"))
    for i, peak in enumerate(peak_labels):
        peak_data = peaks[peak]
        output.append("%10i%s%s\n" % (i,peak,peak_data))

    print "".join(output)
   


if __name__ == "__main__":
    main()
