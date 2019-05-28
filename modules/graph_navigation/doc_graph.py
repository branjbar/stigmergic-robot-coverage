import networkx
from modules.basic_modules.basic import run_query, log

__author__ = 'bijan'
"""
here we construct the document graph and study that
e.g., how blocks can change the number of connected components.
"""


class DocGraph():
    def __init__(self):
        self.block_dict = {}  # block_dict = {block_id: size}
        self.document_dict = {}  # document_dict = {document_id: [block_id1, block_id2, ...]}
        self.reference_dict = {}  # reference_dict = {ref_id: document_id}
        self.component_dict = {}
        self.graph = networkx.Graph()  # a graph. nodes: refs and blocks, edges: family relations and block membership

    def collect_data(self):
        """
        collect required data for constructing the graph
        :return:
        """

        query = "SELECT id, block_id, register_id FROM links_based.all_persons_2014 limit 1000000"

        cur = run_query(query)
        for c in cur:
            ref_id = c[0]
            block_key = c[1]
            doc_id = c[2]

            self.block_dict[block_key] = self.block_dict.get(block_key, []) + [doc_id]


            if self.document_dict.get(doc_id):
                self.document_dict[doc_id]['block_id'].append(block_key)
            else:
                self.document_dict[doc_id] = {'block_id': [block_key], 'component_id': doc_id}

            self.component_dict[doc_id] = [doc_id]

    def add_blocking_nodes(self, threshold):
        for block_key in self.block_dict.keys():
            if len(self.block_dict[block_key]) < threshold:
                ref_doc = self.block_dict[block_key][0]
                ref_comp = self.document_dict[ref_doc]['component_id']
                for doc_id in self.block_dict[block_key][1:]:
                    new_comp = self.document_dict[doc_id]['component_id']
                    if new_comp != ref_comp:
                        for new_doc in self.component_dict[new_comp]:
                            if new_doc != ref_doc:
                                self.document_dict[new_doc]['component_id'] = ref_comp
                                self.component_dict[ref_comp].append(new_doc)

                        self.component_dict.pop(new_comp)
                self.component_dict[ref_comp] = list(set(self.component_dict[ref_comp]))



    def construct_graph(self, threshold):
        """
        construct the graph from collected data
        :return:
        """
        for doc_id in self.document_dict.keys():
            self.graph.add_node(doc_id, node_type='d')

        for block_key in self.block_dict.keys():
            if len(self.block_dict[block_key]) < threshold:
                self.graph.add_node(block_key, node_type='b')

                for doc_id in self.block_dict[block_key]:
                    self.graph.add_edge(block_key, doc_id)


    def get_number_of_connected_components(self):
        # return len(self.component_dict.keys())
        return networkx.number_connected_components(self.graph)

if __name__ == '__main__':

    # for thresh in xrange(100):
    #     my_graph = DocGraph()
    #     print thresh,
    #     my_graph.collect_data()
    #     print ', ',
    #
    #     my_graph.add_blocking_nodes(thresh)
    #     print my_graph.get_number_of_connected_components()




    # for thresh in xrange(100):
    my_graph = DocGraph()
        # log("collecting data")
    my_graph.collect_data()
        # log("collecting data finished")
        # my_graph.add_blocking_nodes(thresh)
        # print str(thresh) + ', ' + str(my_graph.get_number_of_connected_components())


    # print my_graph.get_number_of_connected_components()

    for thresh in xrange(100):
        my_graph.graph = networkx.Graph()
        my_graph.construct_graph(thresh + 2)
        print str(thresh + 2) + ', ' + str(my_graph.get_number_of_connected_components())


