import httplib
import json
import thread
#import sublime


class SynonymManager(object):
    def __init__(self, coding='json'):
        self.api_version = "2"
        self.coding = coding

    def get_synonyms(self, word, api_key="", callback=None, asynchronous=False):
        self.key = api_key
        if asynchronous:
            thread.start_new_thread(self.threaded_api_request, (word, callback,))
        else:
            return self._get_syns(word)

    def threaded_api_request(self, word, callback):
        synonym_list = self._get_syns(word)
        callback(synonym_list)

    def _get_syns(self, word):
        synonym_list = []
        request = '/api/%s/%s/%s/%s' % \
                    (self.api_version, self.key, word, self.coding)
        #sublime.message_dialog(request)
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
        else:
            synonym_list = response.status
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
