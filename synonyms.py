import sublime
import sublime_plugin
import synonyms_request


KEY_SETTINGS_NAME = "synonyms_api_key.settings"


def save_api_key(key):
    #settings = sublime.Settings()
    api_key_settings = sublime.load_settings(KEY_SETTINGS_NAME)
    api_key_settings.set("key", key)
    sublime.save_settings(KEY_SETTINGS_NAME)


def get_api_key(user_query=True):
    api_key_settings = sublime.load_settings(KEY_SETTINGS_NAME)
    api_key = api_key_settings.get("key", "")
    if api_key == "" and user_query:
        sublime.message_dialog("There is no API key set yet. Enter a valid key now. You can register for a key under http://words.bighugelabs.com/getkey.php for free.")
        sublime.active_window().show_input_panel("Synonym API key:", "", save_api_key, None, None)
    return api_key


class ChangeSynonymsKeyCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        current_key = get_api_key(user_query=False)
        sublime.active_window().show_input_panel("New Synonym API key:", current_key, save_api_key, None, None)


class SynonymsCommand(sublime_plugin.TextCommand):

    def run(self, edit, sub_words=False):
        api_key = get_api_key()
        if api_key == "":
            return

        selections = self.view.sel()  # gives a RegionSet
        if len(selections) > 1:
            return  # multiple selections are not supported

        separatorString = self.view.settings().get('word_separators') + u" \n\r"
        wordRegion = self.view.word(selections[0])
        currentWord = self.view.substr(wordRegion).strip(separatorString)

        self.view.sel().add(wordRegion)

        synManager = synonyms_request.SynonymManager()
        syns = synManager.get_synonyms(currentWord, api_key=api_key)

        self.region = wordRegion
        self.callback(syns)  # synonyms_request is prepared for async requests

    def callback(self, syns):
        self.syns = syns
        if type(syns) != list:
            if syns == 500:
                sublime.message_dialog("Either you reached the API request limit for this month or your key is inactive. Try Sublime command menue 'Change synonyms API key' to change it.")
                return
            elif syns == 404:
                sublime.message_dialog("No synonyms found.")
                return
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
