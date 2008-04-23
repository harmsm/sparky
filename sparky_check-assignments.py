#!/usr/bin/env python
__description__ = \
"""
sparky_check-assignments.py

Do a couple of simple checks on the assignments of a spectrum given the
statistics for assignments of identical atom types in many NMR spectra.
"""
__author__ = "Michael J. Harms"
__date__ = "080423"
__usage__ = "sparky_check-assignments.py assignment_file [stat_file]"

import os, sys

def parseStats(stats_file):
    """
    Parse a chemical shift statistics file from brmb.
    """

    # Read in file and remove comments and blank lines 
    f = open(stats_file,'r')
    lines = f.readlines()
    f.close()
    lines = [l.split() for l in lines if l[0] != "#" and l.strip() != ""]
  
    stats = [("%s %s" % (l[0],l[1]),(float(l[6]),float(l[7]))) for l in lines]
   
    return dict(stats)

def sparkyCheckAssignments(assignment_file,stats,resonance="w2"):
    """
    """

    f = open(assignment_file,'r')
    lines = f.readlines()
    f.close()
    lines = [l for l in lines if l[0] != "#" and l.strip() != ""]

    # Parse header and column names
    header = lines[0].split()    
    columns = [l.split() for l in lines[1:]]
    col_dict = dict([(k,i+1) for i, k in enumerate(header)])
  
    # Read assignments input data 
    try: 
        residue_index = col_dict["residue"]
        residues = [int(c[residue_index]) for c in columns]

        assgn_index = col_dict["assgn_atoms"]
        assgn = [c[assgn_index] for c in columns]
        
        aa_index = col_dict["aa"]
        aa = [c[aa_index] for c in columns]
        
        atoms_index = col_dict["atoms"]
        atoms = [c[atoms_index] for c in columns]

        N = range(len(residues))

    except KeyError:
        err = "%s is not formatted correctly!" % assignment_file
        raise SparkyCheckAssignmentsError(err)

    # Read actual resonance data (separate check because user can specify 
    # resonance on command line)
    try:
        resonance_index = col_dict[resonance]
        res_values = [float(c[resonance_index]) for c in columns]
    except KeyError:
        err = "%s does not contain data for resonance %s" % \
            (assignment_file,resonance)
        raise SparkyCheckAssignmentsError(err)


    # Check for non-sequential assignment residues
    assgn_num = [[int(x.split("-")[0][3:]) for x in a.split(",")]
                 for a in assgn]
    out_of_order = [(residues[i],aa[i],assgn[i])
                    for i in N if (assgn_num[i][0] != residues[i]+1) or 
                                  (assgn_num[i][1] != residues[i]+1)] 

    # Find residues that have more than one aa name
    res_dict = dict([(residues[i],aa[i]) for i in N])
    double_name = [(residues[i],aa[i],res_dict[residues[i]]) for i in N 
                   if aa[i] != res_dict[residues[i]]]

    # Make sure that all of the atoms have standard amino acid and atom names
    possible_atoms = stats.keys() 
    atom_keys = [(i,"%s %s" % (aa[i],atoms[i])) for i in N]
    bad_atoms = [a for a in atom_keys if a[1] not in possible_atoms]

    # Check for ppm values different by more than a standard deviation from 
    # average.
    atom_keys = [a for a in atom_keys if a not in bad_atoms]
    deviations = [abs(res_values[a[0]] - stats[a[1]][0]) for a in atom_keys]
    strange_ppm = [a for i, a in enumerate(atom_keys)
                   if deviations[i] > stats[a[1]][1]]
 
    # Generate human-readable output
    out = ["Automated assignment checking for:\n    %s\n\n" % \
           os.path.abspath(assignment_file)] 
    out.append("Possible non-sequential assignments:\n")
    out.extend(["    %i %s, %s\n" % o for o in out_of_order])
    out.append("\n")
    out.append("Residue numbers with multiple amino acid names:\n")
    out.extend(["    %i %s, %s\n" % d for d in double_name])
    out.append("\n")
    out.append("Unrecognized amino acid/atom pairs:\n")
    out.extend(["    %i %s\n" % (residues[a[0]],a[1]) for a in bad_atoms])
    out.append("\n")
    out.append("Chemical shifts greater than 1 std from average:\n")
    out.extend(["    %i %s, %.3F (Avg: %.3F +/- %.2F)\n" % \
               (residues[a[0]],a[1],res_values[a[0]],
                stats[a[1]][0],stats[a[1]][1]) for a in strange_ppm])
    out.append("\n")

    return "".join(out)
    
def main():
    """
    Function to call if run from command line.
    """

    print __file__
    try:
        assignment_file = sys.argv[1]
    except IndexError:
        print __usage__
        sys.exit()

    try:
        stat_file = sys.argv[2]
    except IndexError:
        script_dir = os.path.split(__file__)[0]
        stat_file = os.path.join(script_dir,"bmrb_chemical-shift-stats.txt")

    stats = parseStats(stat_file)
    log = sparkyCheckAssignments(assignment_file,stats)


    #print log


if __name__ == "__main__":
    main()
