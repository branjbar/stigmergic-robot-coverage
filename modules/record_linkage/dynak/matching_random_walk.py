"""
    This code builds a huge graph in which each node is an individual and edges are either because of family relations
     or blocking keys.

At the end the exported csv file can be imported in mysql using:
    LOAD DATA INFILE '/Users/Bijan/sandbox/Eclipse_Projects/linkPy/data/matching_random_walk/matches_random_walk_10000.csv'
    INTO TABLE miss_matches_random_walk FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n';

"""
import matplotlib

matplotlib.use('TkAgg')
import networkx
from modules.basic_modules import basic
from modules.basic_modules.basic import log
from modules.record_linkage.dynak.visualize import get_family_edge
import os
import heapq  # for finding the k largest element
from modules.basic_modules.random_walk import RandomWalk
from modules.basic_modules import random_walk
import pickle
import threading
import time

FILE_NAME_1 = "../../../data/matching_random_walk/matches_random_walk_%d.csv"
FILE_NAME_2 = "/Users/bijan/sandbox/stigmergic-robot-coverage/data/matching_random_walk/matches_random_walk_%d.csv"

MAX_BLOCK_SIZE = 100  # the maximum block size which is acceptable
MAX_REFERENCES = 6000000
DEBUG = False  # if true then does extra prints
RESTART = .3  # random walk restart
MAXIMUM_NUMBER_OF_THREADS = 2


class EntityResolution():
    def __init__(self):

        self.block_dict = {}  # block_dict = {block_id: [ref1_id, ref2_id, ...]}
        self.document_dict = {}  # document_dict = {document_id: [ref1_id, ref2_id, ...]}
        self.reference_dict = {}  # reference_dict = {ref_id: document_id}

        self.graph = networkx.Graph()  # a graph. nodes: refs and blocks, edges: family relations and block membership
        self.graphs = [self.graph]  # a list of graph components
        self.graphs_index = 0  # the index of graph in graphs that is under study
        self.random_walk = None


        # some parameters for exporting message in csv file
        self.export_message = ''  # the message which should be saved in csv file
        self.message_counter = 1290
        try:
            try:
                os.remove(FILE_NAME_1 % MAX_REFERENCES)  # to be sure data will not be appended to a non-empty file
            except:
                os.remove(FILE_NAME_2 % MAX_REFERENCES)  # to be sure data will not be appended to a non-empty file
        except: pass

    def load_dictionary(self, from_file=False, limit=1000):
        """
            loads the required dictionaries that contain useful information about blocks and documents


        """
        if not from_file:

            log("start gathering blocks and documents")


            # let's keep it as light as possible
            block_query = """
                            SELECT id, block_id, register_id
                            FROM links_based.all_persons_2014
                            LIMIT %d
                          """ % limit
            cur = basic.run_query(block_query)

            for c in cur.fetchall():
                ref_id = c[0]
                block_id = c[1]
                register_id = c[2]
                self.reference_dict[ref_id] = register_id
                if block_id != 1888:
                    self.block_dict[block_id] = self.block_dict.get(block_id, []) + [ref_id]
                self.document_dict[register_id] = self.document_dict.get(register_id, []) + [ref_id]

    def load_graph(self, from_file=False):
        """
        generates a graph from the dictionaries
        """

        if not from_file:
            log("loading data")
            self.load_dictionary(False, MAX_REFERENCES)

            log("start building the graph based on blocks")

            # add block edges first
            for block_id in self.block_dict.keys():
                block_ref_list = self.block_dict[block_id]
                if len(block_ref_list) < MAX_BLOCK_SIZE:  # to avoid huge graphs for now
                    block_node_name = '#block_%d' % block_id
                    self.graph.add_node(block_node_name, type="block")
                    for reference in block_ref_list:
                        self.graph.add_node(reference, block_id=block_id)
                        self.graph.add_edge(reference, block_node_name)

            log("start adding the family relations")

            for node in self.graph.nodes():
                if not self.graph.node[node].get('type'):
                    edge_list = get_family_edge(self.document_dict[self.reference_dict[node]])
                    for e in edge_list:
                        self.graph.add_edge(e[0], e[1])

            # log("exporting graph to file (it might take up to 10 minutes for a big graph!!)")
            # networkx.write_gpickle(self.graph, "../../../data/matching_random_walk/full_graph")
            # log("exporting graph finished")
        else:
            log("importing graph from file")
            self.graph = networkx.read_gpickle("../../../data/matching_random_walk/full_graph")
            log("importing graph from file finished")

    def get_similars(self, reference, restart=.3):
        """ (int, double) -> (dict)
            for a specific reference, reports all the possible matches from co-block references.
        """
        similarity_dict = {}
        random_walk = RandomWalk(self.graphs[self.graphs_index])

        excluded_node = '#block_%d' % self.graph.node[reference]['block_id']
        random_walk.run_intelligent_uniform([reference], restart, excluded_node)
        k_keys_sorted_by_values = heapq.nlargest(100, random_walk.proximity_dict,
                                                 key=random_walk.proximity_dict.__getitem__)
        # here the problem is that many of the similar nodes are not acceptable:
        #   * being equal to the reference
        #   * being in the same document as the reference
        #   * not being in the same block as reference
        #   * some returned similars have a proximity of zero

        for key in k_keys_sorted_by_values:
            if not key == reference \
                    and not self.graph.node[key].get('type') \
                    and self.graph.node[reference].get('block_id') == self.graph.node[key].get('block_id') \
                    and (reference - key > 3 or reference - key < -3) \
                    and random_walk.proximity_dict[key] > 0:
                similarity_dict[key] = random_walk.proximity_dict[key]

        similarity_dict = normalize_dict(similarity_dict)

        return similarity_dict

    def find_matches(self, do_threading=False):
        """
        parses thought all nodes, and reports the potential mathces
        """

        log("starting the random walk")
        # this_graph = self.graphs[self.graphs_index]
        this_graph = self.graph
        if not do_threading:
            log("Single-Thread Matching")
            for node in this_graph:
                if this_graph.node[node].get('block_id'):   # if node is a reference
                    # if not self.message_counter % 1:
                        # log('random_walk on node %s' % node)
                    self.matching_thread(node)

        else:  # if do threading
            log("Multi-Thread Matching is not active!!")

            # for node in this_graph:
            #     if this_graph.node[node].get('block_id'):   # if node is a reference
            #         self.manage_thread(node)

        self.export_results()

    def matching_thread(self, node):

        # log('random_walk on node %s' % node)
        similars_list = self.get_similars(node, RESTART)
        for sim in similars_list.keys():
            self.export_results([node, sim, similars_list[sim]])  # ref1, ref2, score

    # def manage_thread(self, node):
    #     """
    #     a thread that checks a specific reference and saves the results in csv file.
    #     """
    #     thread_limiter = threading.BoundedSemaphore(MAXIMUM_NUMBER_OF_THREADS)
    #
    #     thread_limiter.acquire()
    #     try:
    #
    #         t = threading.Thread(target=self.matching_thread, args=(node,))
    #         t.start()
    #
    #     finally:
    #
    #         thread_limiter.release()

    def export_results(self, message_list=None):
        """
        gets a list of values that stores them in a csv file with comma delimited
        """

        if DEBUG:
            log(message_list)

        if message_list:
            message = '\N,'  # null for using the auto increment
            for msg in message_list:
                message += str(msg) + ','
            message += '\N, restart = %.2f & local_nbrs = %d \n' % (RESTART, random_walk.LOCAL_NEIGHBORHOOD)

            self.export_message += message
            self.message_counter += 1

        try:
            if self.message_counter % 2 == 1 or not message_list:
                with open(FILE_NAME_1 % MAX_REFERENCES, 'a') as csv_file:
                    csv_file.write(self.export_message)
                self.export_message = ''
        except:
            if self.message_counter % 2 == 1 or not message_list:
                with open(FILE_NAME_2 % MAX_REFERENCES, 'a') as csv_file:
                    csv_file.write(self.export_message)
                self.export_message = ''

    def get_statistics(self):
        """
        gets statistics of the constructed graph, such as diameter and size of graph
        """
        print "number of connected components %d" % networkx.number_connected_components(self.graph)
        networkx.number_connected_components(self.graph)
        graphs = networkx.connected_component_subgraphs(self.graph)
        graph_diameter = []
        graph_size = []
        for index, graph in enumerate(graphs):
            print index
            # graph_diameter.append(networkx.diameter(graph))
            graph_size.append(graph.number_of_nodes())
        from numpy import array, histogram
        graph_diameter = array(graph_diameter)
        graph_size = array(graph_size)

        # print "-----GRAPH DIAMETER-----"
        # print 'max is %d' % graph_diameter.max() \
        #       + ', min is %d' % graph_diameter.min() \
        #       + ', average is %d' % graph_diameter.mean() \
        #       + ', std is %d' % graph_diameter.std()

        # print 'freq.', list(histogram(graph_diameter)[0])
        # print 'graph_diameter', list(histogram(graph_diameter)[1])

        print "-----GRAPH SIZE-----"
        print 'max is %d' % graph_size.max() \
              + ', min is %d' % graph_size.min() \
              + ', average is %d' % graph_size.mean() \
              + ', std is %d' % graph_size.std()

        # print 'freq.', list(histogram(graph_size)[0])
        # print 'size', list(histogram(graph_size)[1])

        import csv
        with open("graph_size.csv", "wb") as f:
            writer = csv.writer(f)
            writer.writerows([list(graph_size)])
        with open("graph_diameter.csv", "wb") as f:
            writer = csv.writer(f)
            writer.writerows([list(graph_diameter)])


def normalize_dict(dict):
    """ (dict) --> dict
    gets a dictionary, normalises all values so that they sum to 1
    """
    volume = sum(dict.values())  # initial sum of the values
    dict_n = {key: (dict[key] / volume) for key in dict.keys()}
    return dict_n


def main():

    entity_resolution = EntityResolution()
    entity_resolution.load_graph(False)
    # entity_resolution.find_matches()
    # print entity_resolution.get_similars(1, RESTART)

if __name__ == "__main__":
    main()


