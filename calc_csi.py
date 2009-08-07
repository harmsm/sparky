#!/usr/bin/env python
"""
calc_csi.py

Calculate the chemical shift index of for CA atoms.

Original algorithm taken from program by MS Chimenti.  CSI_DICT taken from
Wishart & Sykes (1994). Methods in Enzymology 239:363-392.
"""
__author__ = "Michael J. Harms"
__date__ = "080516"

import sys

CSI_DICT = {'ALA' : [51.7,53.0],
            'CYS' : [56.3,57.6],
            'ASP' : [53.4,54.7],
            'GLU' : [56.0,57.3],
            'PHE' : [57.4,58.7],
            'GLY' : [44.5,45.8],
            'HIS' : [55.0,56.3],
            'ILE' : [60.7,62.0],
            'LYS' : [56.0,57.3],
            'LEU' : [54.5,55.8],
            'MET' : [54.7,56.0],
            'ASN' : [52.2,53.5],
            'PRO' : [62.5,63.8],
            'GLN' : [55.5,56.8],
            'ARG' : [55.5,56.8],
            'SER' : [57.6,58.9],
            'THR' : [61.5,62.8],
            'VAL' : [61.7,63.0],
            'TRP' : [57.1,58.4],
            'TYR' : [57.5,58.8]}


def readRFile(filename,column_list,data_type):
    """
    Read an R-style data file.
    """

    f = open(filename,'r')
    lines = [l for l in f.readlines() if l[0] != "#" and l.strip() != ""]
    f.close()
    
    # Parse header 
    header = lines.pop(0)
    header = header.split()
    num_columns = len(header)
    header_dict = dict([(c,i) for i, c in enumerate(header)])

    # Make sure all columns are in data file
    header_keys = header_dict.keys()
    for c in column_list:
        if c not in header_keys:
            err = "Column \"%s\" missing from file!" % c
            raise CsiError(err) 

    # Read data from columns
    data = []
    for line in lines:
        columns = line.split()[1:]
        data.append([data_type[i](columns[header_dict[c]])
                    for i, c in enumerate(column_list)])

    # Take only CA atoms
    data = [d for d in data if d[2] == "CA"]

    return data


def doCSI(data):
    """
    Use data in CSI_DATA to calculate chemical shift index.
    """

    out = []
    for d in data:
        csi = CSI_DICT[d[1]]
        if d[3] < csi[0]:
            out.append("beta")
        elif d[3] > csi[1]:
            out.append("alpha")
        else:
            out.append("coil") 

    return out

def main():

    try:
        filename = sys.argv[1]
    except IndexError:
        print "You must specify a file for CSI analysis!"
        sys.exit()

    data = readRFile(filename,["residue","aa","atoms","w2"],[int,str,str,float])

    csi_index = doCSI(data)
    
    out = []
    for i in range(len(data)):
        out.append("%10i%10s%10s%10.3F%10s\n" % 
                   (data[i][0],data[i][1],data[i][2],data[i][3],csi_index[i]))
    out = ["%10i%s" % (i,l) for i,l in enumerate(out)]
    out.insert(0,"%10s%10s%10s%10s%10s%10s\n" % 
               (" ","residue","aa","atom","w2","csi"))

    print "".join(out)


if __name__ == "__main__":
    main()
