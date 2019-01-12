# Keypirinha: a fast launcher for Windows (keypirinha.com)

import re
import os
import subprocess
import keypirinha as kp
import keypirinha_util as kpu

class Zealous(kp.Plugin):
    SECTION_DOCS = 'docs'

    SECTION_MAIN = 'main'

    REGEX_INPUT = r'(\S+)\s(.+)'

    ITEM_CAT = kp.ItemCategory.USER_BASE + 1

    def __init__(self):
        super().__init__()
        self._debug = True

    def on_start(self):
        self._gather_docs()

    def on_catalog(self):
        self.on_start()

    def on_suggest(self, user_input, items_chain):

        input = re.search(self.REGEX_INPUT, user_input)

        if input is None:
            return None

        for docid in self.docs:
            idx, term = input.groups()
            if docid == idx:
                doc = self._get_setting(docid, self.SECTION_DOCS)
                suggestion = self._set_suggestion(docid, doc, term)

                self.set_suggestions(suggestion)

    def _set_suggestion(self, docid, doc, term):
        return [
            self.create_item(
                category = self.ITEM_CAT,
                label = docid + ' : Search ' + doc + ' for ' + term,
                short_desc = doc + ':' + term,
                target = doc + ':' + term,
                args_hint = kp.ItemArgsHint.FORBIDDEN,
                hit_hint = kp.ItemHitHint.IGNORE
            )
        ]

    def _set_error(self, msg):
        return [
            self.create_error_item(
                label = "Error",
                short_desc = msg,
                target = error
            )
        ]

    def on_execute(self, item, action):
        if item.category() != self.ITEM_CAT:
            return

        zeal_exe = self._get_setting('path', self.SECTION_MAIN)
        if not 'zeal.exe' in zeal_exe:
            zeal_exe = os.path.join(zeal_exe, 'zeal.exe')

        if os.path.isfile(zeal_exe):
            try:
                cmd = [zeal_exe]
                cmd.append(item.target())
                subprocess.Popen(cmd, cwd=os.path.dirname(zeal_exe))
            except Exception as e:
                self.dbg("Zeal - (%s)" % (e))
        else:
            self.err('Could not find your %s executable.\n\nPlease edit Zeal.sublime-settings' % (zeal_exe))

    def _gather_docs(self):
        self.docs = self.load_settings().keys(self.SECTION_DOCS)

    def _get_setting(self, setting, section):
        return self.load_settings().get_stripped(
            setting,
            section=section,
            fallback=section
        )

    def on_events(self, flags):
        if flags & kp.Events.PACKCONFIG:
            self.on_start()
