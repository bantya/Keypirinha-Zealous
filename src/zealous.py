import re
import os
import json
import plistlib
import subprocess
import keypirinha as kp
import keypirinha_util as kpu
from .db import get_names

class Zealous(kp.Plugin):
    SECTION_DOCS = 'docs'

    SECTION_MAIN = 'main'

    PLIST_FILE = 'Contents\\Info.plist'

    DB_FILE = 'Contents\\Resources\\docSet.dsidx'

    REGEX_INPUT = r'(\S+)\s(.+)'

    ITEM_CAT = kp.ItemCategory.USER_BASE + 1

    def __init__(self):
        super().__init__()
        self._debug = True

    def on_start(self):
        self._load_settings()
        self._gather_docs()

        package_path = self.get_package_cache_path(True)
        self.docsets_json = os.path.join(package_path, 'docsets.json')

        default_docset_path = kp.package_cache_dir().split('Keypirinha\\Packages')[0] + 'Zeal\\Zeal\\docsets'
        self.docsets_path = self.settings.get_stripped('docset_path', self.SECTION_MAIN, default_docset_path)

        json_data = self._read_json()

        for key in self.docs:
            docset = self.settings.get_stripped(key, self.SECTION_DOCS)
            if docset not in json_data.keys():
                for folder_name in os.listdir(self.docsets_path):
                    plist_path = os.path.join(self.docsets_path, folder_name, self.PLIST_FILE)
                    if os.path.isfile(plist_path):
                        with open(plist_path, 'rb') as fp:
                            pl = plistlib.load(fp)
                            if docset == pl["DocSetPlatformFamily"]:
                                self._save_docsets(docset, folder_name.split('.docset')[0])

    def on_catalog(self):
        self.on_start()

    def on_activated(self):
        print('----------')

    def on_deactivated(self):
        print('----------')

    def on_suggest(self, user_input, items_chain):
        suggestions = []
        input = re.search(self.REGEX_INPUT, user_input)

        if input is None:
            return None

        for docid in self.docs:
            idx, term = input.groups()
            if docid == idx:
                docset = self.settings.get_stripped(docid, self.SECTION_DOCS)
                docset_folder = self._get_docset_folder(docset)
                db_path = self._get_docset_path(docset_folder, self.DB_FILE)

                suggestions.append(self._set_suggestion(docid, docset, term))

                dicta = self._get_entity_names(db_path, term)

                for name in dicta:
                    name = ''.join(name)
                    suggestions.append(self._set_suggestion(docid, docset, name))

                self.set_suggestions(suggestions)

    def _get_docset_folder(self, key):
        data = self._read_json()

        if key in data.keys():
            return data[key]

    def _save_docsets(self, docset, docset_path):
        data = self._read_json()

        data.update({docset: docset_path})

        self._save_json(data)

    def _save_json(self, data):
        with open(self.docsets_json, 'w') as outfile:
            json.dump(data, outfile)

    def _read_json(self):
        if not os.path.isfile(self.docsets_json):
            self._save_json({})

            return {}

        try:
            with open(self.docsets_json) as json_file:
                return json.load(json_file)
        except json.decoder.JSONDecodeError:
            self._save_json({})

            return {}

    def _get_docset_path(self, docset, docfile):
        if not docset.endswith(".docset"):
            docset += '.docset'

        return os.path.join(self.docsets_path, docset, docfile)

    def _get_entity_names(self, doc, term):
        return get_names(doc, term)

    def _set_suggestion(self, docid, doc, term):
        return self.create_item(
            category = self.ITEM_CAT,
            label = docid + ' : ' + term,
            short_desc = doc + ':' + term,
            target = doc + ':' + term,
            args_hint = kp.ItemArgsHint.FORBIDDEN,
            hit_hint = kp.ItemHitHint.IGNORE
        )

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

        zeal_exe = self.settings.get_stripped('path', self.SECTION_MAIN, 'C:\\Program Files\\Zeal')

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
            self.err('Could not find your %s executable.\n\nPlease edit path' % (zeal_exe))

    def _gather_docs(self):
        self.docs = self.load_settings().keys(self.SECTION_DOCS)

    def _load_settings(self):
        self.settings = self.load_settings()

    def on_events(self, flags):
        if flags & kp.Events.PACKCONFIG:
            self.on_start()
