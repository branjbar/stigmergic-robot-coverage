"""
gets required statistics about the random walk algorithm. Here we use the Solr indexing,
though the results are identical to the RWR approach.
"""
import numpy
from modules.record_linkage.hashing import Hashing

__author__ = 'bijan'


class Statistics():
    """
    a general class to get statistics from the matches!

    Final result:
                [      0 4423970  812559  193697   85123   46626   30159   20798   15135
               10881    8208    6134    4772    3610    2698    2121    1698    1306
                 945     806     614     552     401     307     237     216     163
                 142     138      91      84      65      57      53      37      36
                  27      17      18      21      16      10      10      15      14
                   9      14      11       6       6       4       5       4       5
                   3       5       1       1       3       5       2       3       2
                   3       4       1       2       2       2       5       0       3
                   1       2       2       1       0       1       1       1       1
                   0       3       0       0       2       1       0       1       0
                   1       0       0       0       0       1       1       2       0]
    """
    def __init__(self):
        self.unique_blocks = {}
        self.hashing = Hashing()

    def get_number_of_unique_block_ids(self):
        start = 0
        num_found = 10000000
        while start <= num_found:
            response = self.hashing.s.query('id:*', rows=10000, start=start, fields="id, blockKeys")
            num_found = response.numFound
            for r in response.results:
                if int(r.get('id')) < 30000000:
                    for b in r.get('blockKeys', []):
                        self.unique_blocks[b] = self.unique_blocks.get(b, 0) + 1
            print start
            start += 10000

        print numpy.histogram(self.unique_blocks.values(), bins=xrange(100))[0]
        print "%d unique keys collected." % (len(self.unique_blocks))
        return self.unique_blocks


if __name__ == "__main__":
    stat = Statistics()
    blocks = stat.get_number_of_unique_block_ids()

