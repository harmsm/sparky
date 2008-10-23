#!/usr/bin/env python
__description__ = \
"""
sparky_rename-peaks.py 

Rename peaks in Sparky .save files using rules specified in input file.  
"""

__author__ = "Michael J. Harms"
__date__ = "080409"
__usage__ = "sparky_rename-peaks.py peak-rules $1.save $2.save ... $n.save"

import os, sys, shutil

class SparkyRenamePeaksError(Exception):
    """
    General error class for this module.
    """

    pass

def readPeakRules(peak_rules_file):
    """
    Read in peak rules file of format:
   
    old_peak1-->new_peak1
    old_peak2-->new_peak2
    ...

    Comment lines (#) and blank lines are ignored.  It is assumed that peak
    names do not have "-->" or spaces in them.
    """ 

    f = open(peak_rules_file,'r')
    peak_rules = f.readlines()
    f.close()
   
    peak_rules = [l for l in peak_rules if l[0] != "#" and l.strip() != ""] 
    
    try:
        peak_dict = [l.split("-->") for l in peak_rules]
        peak_dict = dict([(x[0].strip(),x[1].strip()) for x in peak_dict])
    except:
        err = "%s contains mangled data!" % peak_rules_file
        raise SparkyRenamePeaksError(err)

    return peak_dict

def convertSparkyFile(sparky_file,peak_dict):
    """
    Rename peaks in sparky_file using rules in peak_dict. 
    """

    # Copy sparky_file to backup file and read data
    f = open(sparky_file,'r')
    sparky = f.readlines()
    f.close()

    # Alter relevant lines
    peak_keys = peak_dict.keys()
    for line_number, line in enumerate(sparky):

        # Alter "rs" entries
        if line[0:3] == "rs ":
            column = line[4:].split("|")
            
            altered = False
            if column[0] in peak_keys:
                column[0] = peak_dict[column[0]]
                altered = True
            if column[3] in peak_keys:
                column[3] = peak_dict[column[3]]
                altered = True
           
            if altered:
                new_line = ["|%s" % c for c in column]
                new_line = "rs %s" % ("".join(new_line))
                sparky[line_number] = new_line

        # Alter "label" entries
        possible_atoms = ["N-HN","NE1-HE1","N"]
        if line[0:6] == "label ":
          
            # Try to separate atoms from actual peak label 
            atoms_index = 0
            success = False
            while not success and atoms_index <= len(possible_atoms):
                try:
                    atoms = possible_atoms[atoms_index]
                    peak_name = line[6:line.index(atoms)]
                    success = True
                except ValueError:
                    atoms_index += 1
                except IndexError:
                    err = "Error parsing line!:\n%s" % line
                    raise SparkyRenamePeaksError(err)

 
            if not success:
                err = "Atoms on line: \"%s\" not recognized!" % line
                raise SparkyRenamePeaksError(err)            
    
            if peak_name in peak_keys:
                peak_name = peak_dict[peak_name]
                new_line = "label %s%s\n" % (peak_name,atoms)
                sparky[line_number] = new_line

    # Write output
    g = open(sparky_file,'w')
    g.writelines(sparky)
    g.close()


def main():
    """
    If called from command line...
    """

    # Parse command line
    try:
        peak_rules_file = sys.argv[1]
        sparky_files = sys.argv[2:]
    except IndexError:
        print __usage__
        sys.exit()

    # Read in peak conversion rules
    peak_dict = readPeakRules(peak_rules_file)
   
    # Make sure that sparky files exist 
    file_check = [os.path.isfile(f) for f in sparky_files]
    if False in file_check:
        print "Not all specified sparky save files exist!"
        sys.exit()
   
    sparky_files.sort() 
    for sparky_file in sparky_files:
        print sparky_file
        convertSparkyFile(sparky_file,peak_dict)    
        



if __name__ == "__main__":
    main()
