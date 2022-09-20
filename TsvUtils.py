"""
Reading and writing TSV files that are TTL-compatible

(c) 2022 Fabian M. Suchanek
"""

import gzip
import os
import sys
import evaluator
import Prefixes

TEST=True

##########################################################################
#             Reading lines of a file
##########################################################################

def linesOfFile(file, message="Parsing"):
    """ Iterator over the lines of a GZ or text file, with progress bar """
    print(message,"...", end="", flush=True)
    totalNumberOfDots=60-len(message)
    coveredSize=0
    printedDots=0
    fileSize=os.path.getsize(file)
    isGZ=file.endswith(".gz")
    if isGZ:
        fileSize*=20
    with (gzip.open(file, mode='rt', encoding='UTF-8') if isGZ else open(file, mode='rt', encoding='UTF-8')) as input:
        for line in input:
            coveredSize+=len(line)
            while coveredSize / fileSize * totalNumberOfDots > printedDots:
                print(".", end="", flush=True)
                printedDots+=1
            yield line
    while coveredSize / fileSize * totalNumberOfDots > printedDots:
        print(".", end="", flush=True)
        printedDots+=1
    print("done")

##########################################################################
#             TSV files
##########################################################################

def tsvTuples(file, message="Parsing"):
    """ Iterates over the tuples in a TSV file"""
    for line in linesOfFile(file, message):
        if not line.startswith("#") and not line.startswith("@"):
            yield line.rstrip().split("\t")

class TsvFileWriter(object):
    """ To be used in a WITH...AS clause to write facts to TSV files"""
    def __init__(self, file_name):
        self.file_name = file_name
      
    def __enter__(self):
        self.file = open(self.file_name, "tw", encoding="utf=8")
        for p in Prefixes.prefixes:
            self.file.write("@prefix "+p+": <"+Prefixes.prefixes[p]+"> .\n")
        return self
        
    def write(self, *args):
        for i in range(0,len(args)-1):
            self.file.write(args[i] if args[i] else '')
            self.file.write("\t")
        self.file.write(args[-1] if args[-1] else '')
        self.file.write("\n")
  
    def writeFact(self, subject, predicate, object):
        self.write(subject, predicate, object, ".")
        
    def __exit__(self, *exceptions):
        self.file.close()
        
if TEST and __name__ == '__main__':
    print("Test run of TsvFile...")
    with TsvFileWriter("test-data/tsvUtils/test-output.tsv") as out:
        for line in tsvTuples("test-data/tsvUtils/test-input.tsv"):
            out.writeFact(line[0], line[1], line[2])
    print("done")
    evaluator.compare("test-data/tsvUtils/test-output.tsv", "test-data/tsvUtils/test-input.tsv")