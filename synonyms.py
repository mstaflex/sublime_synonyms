import sublime
import sublime_plugin
import synonyms_request


KEY_SETTINGS_NAME = "synonyms_api_key.settings"


MESSAGE_NO_SYN_FOUND = "No synonyms found."
MESSAGE_ONLY_ONE_SELECTION = "Please select just one word for lookup."
MESSAGE_WRONG_KEY = "Either you reached the API request limit for this month or your key is inactive. Try Sublime command menue 'Change synonyms API key' to change the key."
MESSAGE_NO_KEY = "There is no API key set yet. Enter a valid key now. You can register for a key under http://words.bighugelabs.com/getkey.php for free."


def save_api_key(key):
    #settings = sublime.Settings()
    api_key_settings = sublime.load_settings(KEY_SETTINGS_NAME)
    api_key_settings.set("key", key)
    sublime.save_settings(KEY_SETTINGS_NAME)


def get_api_key(user_query=True):
    api_key_settings = sublime.load_settings(KEY_SETTINGS_NAME)
    api_key = api_key_settings.get("key", "")
    if api_key == "" and user_query:
        sublime.message_dialog(MESSAGE_NO_KEY)
        sublime.active_window().show_input_panel("Synonym API key:", "", save_api_key, None, None)
    return api_key


def get_selected_region(view):
    selections = view.sel()  # gives a RegionSet
    if len(selections) > 1:
        return  # multiple selections are not supported
    wordRegion = view.word(selections[0])
    return wordRegion


def get_selected_word(view):
    region = get_selected_region(view)
    separatorString = view.settings().get('word_separators') + u" \n\r"
    currentWord = view.substr(region).strip(separatorString)
    # view.sel().add(region)  # to select the current word
    return currentWord


class ChangeSynonymsKeyCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        current_key = get_api_key(user_query=False)
        sublime.active_window().show_input_panel("New Synonym API key:", current_key, save_api_key, None, None)


class SynonymsCommand(sublime_plugin.TextCommand):
    def run(self, edit, sub_words=False):
        api_key = get_api_key()
        if api_key == "":
            sublime.message_dialog(MESSAGE_ONLY_ONE_SELECTION)
            return
        currentWord = get_selected_word(self.view)
        synManager = synonyms_request.SynonymManager()
        syns = synManager.get_synonyms(currentWord, api_key=api_key)
        self.callback(syns)  # synonyms_request is prepared for async requests

    def callback(self, syns):
        self.syns = syns
        if type(syns) != list:
            if syns == 500:
                sublime.message_dialog(MESSAGE_WRONG_KEY)
                return
            elif syns == 404:
                sublime.message_dialog(MESSAGE_NO_SYN_FOUND)
                return
        if len(syns) == 0:
            sublime.message_dialog(MESSAGE_NO_SYN_FOUND)
        self.view.window().show_quick_panel(syns, self.insert_syn, sublime.MONOSPACE_FONT)

    def insert_syn(self, choice):
            if choice == -1:
                return
            region = get_selected_region(self.view)
            edit = self.view.begin_edit()
            self.view.erase(edit, region)
            startloc = self.view.sel()[-1].end()
            self.view.insert(edit, startloc, self.syns[choice])
            self.view.end_edit(edit)
# puppet
