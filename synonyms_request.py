import httplib
import json
import thread


class SynonymManager(object):

    def __init__(self, coding='json'):
        self.version = "2"
        self.key = ""
        self.coding = coding

    def get_synonyms(self, word, callback=None, asynchronous=False):
        if asynchronous:
            thread.start_new_thread(self.threaded_api_request, (word, callback,))
        else:/Users/mflex/Library/Application Support/Sublime Text 2/Packages/User/user.sublime-commands
            return self._get_syns(word)

    def threaded_api_request(self, word, callback):
        synonym_list = self._get_syns(word)
        callback(synonym_list)

    def _get_syns(self, word):
        synonym_list = []
        request = '/api/%s/%s/%s/%s' % \
                    (self.version, self.key, word, self.coding)
        conn = httplib.HTTPConnection("words.bighugelabs.com")
        conn.request("GET", request)
        response = conn.getresponse()
        if response.status == 200:
            data = response.read()
            if self.coding == 'json':
                parsed_request = json.loads(data)
                if u'noun' in parsed_request and \
                    u'syn' in parsed_request[u'noun']:
                    synonym_list = parsed_request[u'noun'][u'syn']
        conn.close()
        return synonym_list

if __name__ == '__main__':
    import time

    def print_list(liste):
        print liste[0]

    s = SynonymManager()
    s.get_synonyms("man", print_list)
    # sleep has to be called otherwise the main process closes down
    # and with it the thread
    time.sleep(2)
