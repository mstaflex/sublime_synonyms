import sublime
import sublime_plugin
import synonyms_request


class SynonymsCommand(sublime_plugin.TextCommand):

    def run(self, edit, sub_words=False):
        selections = self.view.sel()  # gives a RegionSet
        if len(selections) > 1:
            return  # multiple selections are not supported

        separatorString = self.view.settings().get('word_separators') + u" \n\r"
        wordRegion = self.view.word(selections[0])
        currentWord = self.view.substr(wordRegion).strip(separatorString)

        self.view.sel().add(wordRegion)

        synManager = synonyms_request.SynonymManager()
        syns = synManager.get_synonyms(currentWord)

        self.region = wordRegion
        self.callback(syns)  # synonyms_request is prepared for async requests

    def callback(self, syns):
        self.syns = syns
        self.view.window().show_quick_panel(syns, self.insert_syn, sublime.MONOSPACE_FONT)

    def insert_syn(self, choice):
            if choice == -1:
                return
            edit = self.view.begin_edit()
            self.view.erase(edit, self.region)
            startloc = self.view.sel()[-1].end()
            self.view.insert(edit, startloc, self.syns[choice])
            self.view.end_edit(edit)
# creature
