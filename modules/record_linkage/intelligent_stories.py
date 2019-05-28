__author__ = 'bijan'

import solr


class Story():
    def __init__(self):
        """
        initializes the Solr connection
        :return:
        """
        self.s = solr.SolrConnection('http://localhost:8983/solr')
        self.commit_counter = 0
        self.commit_number = 0
        self.current_document_id = 2846095

        self.unique_blocks = []

    def get_blocking_keys(self):
        unique_blocks = []
        start = 0
        num_found = 10000000
        while start <= num_found:
            response = self.s.query('id:30*', rows=100, start=start, fields="blockKeys")
            num_found = response.numFound
            for r in response.results:
                for b in r.get('blockKeys', []):
                    if not b in self.unique_blocks:
                        self.unique_blocks.append(b)
            start += 100
        print "%d unique keys collected. Last key: %s" % (len(self.unique_blocks) , self.unique_blocks[-1])

    def find_interesting_stories(self):
        count = 0
        for block_key in self.unique_blocks:
            flag_n = False
            flag_c = False
            response = self.s.query('blockKey=' + block_key, fields="id")
            if response.numFound > 1 and block_key.split('_')[2:4] != block_key.split('_')[8:10] and not '>' in block_key:
                for result in response.results:
                    if int(result['id']) < 30000000:
                        flag_c = True
                    else:
                        flag_n = True
                if flag_c and flag_n:
                    print count, block_key, response.numFound
                    count += 1

if __name__ == '__main__':
    story = Story()
    story.get_blocking_keys()
    story.find_interesting_stories()
