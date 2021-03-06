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
        if type(syns) != dict:
            if syns == 500:
                sublime.message_dialog(MESSAGE_WRONG_KEY)
                return
            else:  # 404 or anathing else
                sublime.message_dialog(MESSAGE_NO_SYN_FOUND)
                return

        word_list = []
        allowed_categories = ['noun', 'verb', 'adjective', 'adverb']
        for category in allowed_categories:
            if category in syns:
                word_list.append(category[0].upper() + category[1:] + ':')
                for word in syns[category]:
                    word_list.append(' ' + word)
        self.syns = word_list
        self.view.window().show_quick_panel(word_list, self.insert_syn, sublime.MONOSPACE_FONT)

    def insert_syn(self, choice):
            if choice == -1:
                return
            selected_word = self.syns[choice]
            selected_word = ''.join(e for e in selected_word if e.isalnum())
            if selected_word.lower() in \
                ['noun', 'adjective', 'verb', 'adverb']:
                return
            currentWord = get_selected_word(self.view)
            region = get_selected_region(self.view)
            edit = self.view.begin_edit()
            self.view.erase(edit, region)
            startloc = self.view.sel()[-1].end()
            # copy capital first letters
            if currentWord[0].isupper():
                selected_word = selected_word[0].upper() + selected_word[1:]
            self.view.insert(edit, startloc, selected_word)
            self.view.end_edit(edit)
# puppet
