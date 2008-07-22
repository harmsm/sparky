__description__ = \
"""
A set of classes useful for reading sparky .save files.
"""
__author__ = "Michael J. Harms"
__date__ = "080425"

import os, sys

class SparkyError(Exception):
    """
    General error class for this module.
    """

    pass

class SparkyPeak:
    """
    A class to hold an individual peak.
    """

    def __init__(self,peak_lines,dimension):
        """
        Use dimension to decide which parser to use on the data in peak_lines.
        """
    
        # Available parsers
        self._parse_dict = {2:self.parse2D,
                            3:self.parse3D}
        
        # Parse data using correct parser
        self.dimension = dimension
        try:
            self.parser = self._parse_dict[self.dimension]
        except KeyError:
            err = "Dimension \"%s\" is not valid!" % dimension
            raise SparkyError(err)

        try:
            self.parser(peak_lines)
        except (ValueError,IndexError):
            err = "Syntax error!  Peak could not be processed!\n\n %s"
            err = err % "".join(peak_lines)
            raise SparkyError(err) 


    def parseCommon(self,peak_lines):
        """
        Parse peak data common to experiments of all dimensionality.
        """

        self.hash = [l[0:3] for l in peak_lines]
        
        # Peak height 
        hei = peak_lines[self.hash.index("hei")][7:].split()
        self.height = float(hei[1])

        # Peak integral
        try:
            integral = peak_lines[self.hash.index("int")][9:].split()
            self.integral = float(integral[0])
        except ValueError:
            self.integral = None
        
        # Peak note
        try:
            note = peak_lines[self.hash.index("not")][5:].strip()
            note = note[1:-1]   # remove trailing quotes
            self.note ="\"%s\"" % note
        except ValueError:
            self.note = None



    def parse2D(self,peak_lines):
        """
        Parse a 2-dimensional peak.
        """

        self.parseCommon(peak_lines)

        # Peak label
        try:
            self.labeled = True
            rs = peak_lines[self.hash.index("rs ")][4:].split("|")
            self.aa = [rs[0][0:3],rs[3][0:3]]
            self.res_num = [int(rs[0][3:]),int(rs[3][3:])]
            self.atoms = [rs[1],rs[4]]
        except ValueError:
            self.labeled = False      
 
        # Peak position 
        pos = peak_lines[self.hash.index("pos")][4:].split()
        self.position = [float(pos[0]),float(pos[1])]
       

    def parse3D(self,peak_lines):
        """
        Parse a 3-dimensional peak.
        """
        
        self.parseCommon(peak_lines)

        # Peak label
        try:
            self.labeled = True
            rs = peak_lines[self.hash.index("rs ")][4:].split("|")
            self.aa = [rs[0][0:3],rs[3][0:3],rs[6][0:3]]
            self.res_num = [int(rs[0][3:]),int(rs[3][3:]),int(rs[6][3:])]
            self.atoms = [rs[1],rs[4],rs[7]]
        except ValueError:
            self.labeled = False
 
        # Peak position 
        pos = peak_lines[self.hash.index("pos")][4:].split()
        self.position = [float(pos[0]),float(pos[1]),float(pos[1])]
       
        
class SparkyExperiment:
    """
    Class to hold a set of sparky peaks extracted from a sparky .save file.
    """

    def __init__(self,save_file,skip_unlabeled=True):
        """
        Read in a file, decide on the experiment dimensions, and generate a
        list of instances of SparkyPeak (self.peak_list).
        """

        # Load file
        if not os.path.isfile(save_file):
            err = "File \"%s\" does not exist!" % save_file
            raise SparkyError(err)
        self.save_file = save_file 
        f = open(self.save_file,'r')
        lines = f.readlines()
        f.close() 

        # Grab dimensionality of experiment
        dim_line = [i for i, l in enumerate(lines) if l[0:9] == "dimension"][0]
        dimension = int(lines[dim_line][9:])
       
        # Make a list of the starting and ending line of each peak
        peak_lines = [i for i, l in enumerate(lines) if l[0:9] == "type peak"]
        end_ornament = [i for i, l in enumerate(lines)
                        if l[0:14] == "<end ornament>"]
        peak_lines.append(end_ornament[0])
        peak_lines = [(peak_lines[i-1],peak_lines[i])
                      for i in range(1,len(peak_lines))]

        # Create list of instances of SparkyPeak for each peak in file.
        self.peak_list = []             
        for peak in peak_lines:
            indiv_peak = lines[peak[0]:peak[1]]
            self.peak_list.append(SparkyPeak(indiv_peak,dimension))

        # Remove unlabeled peaks if requested
        if skip_unlabeled:
            self.peak_list = [p for p in self.peak_list if p.labeled]

                


def main():
    """
    A testing function that can be called from comand line.
    """

    try:
        input_file = sys.argv[1]
    except IndexError:
        print "specify sparky .save file"
        sys.exit()

    experiment = SparkyExperiment(input_file)
    for p in experiment.peak_list:
        if p.labeled:
            print p.position, p.atoms, p.aa


if __name__ == "__main__":
    main()
