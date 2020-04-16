# Copyright 2016 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import webbrowser
import subprocess

from adapt.intent import IntentBuilder
from adapt.tools.text.tokenizer import EnglishTokenizer

from mycroft import MycroftSkill, intent_handler
from urllib.parse import quote
from gi.repository import Gio as gio

IFL_TEMPLATE = 'http://www.google.com/search?&sourceid=navclient&btnI=I&q=%s'


class DesktopLauncherSkill(MycroftSkill):
    def __init__(self):
        super().__init__()
        self.appmap = {}

    def initialize(self):
        tokenizer = EnglishTokenizer()

        for app in gio.app_info_get_all():
            name = app.get_name().lower()
            if name is None:
                # Likely an empty .desktop entry, skip it
                continue
            entry = [app]
            tokenized_name = tokenizer.tokenize(name)[0]

            if name in self.appmap:
                self.appmap[name] += entry
            else:
                self.appmap[name] = entry

            self.register_vocabulary(name, 'Application')
            if name != tokenized_name:
                self.register_vocabulary(tokenized_name, 'Application')
                if tokenized_name in self.appmap:
                    self.appmap[tokenized_name] += entry
                else:
                    self.appmap[tokenized_name] = entry

    @intent_handler(IntentBuilder('LaunchDesktopApplicationIntent')
                    .require('LaunchKeyword')
                    .require('Application'))
    def handle_launch_desktop_app(self, message):
        """Launch a dektop application using Desktop file."""
        app_name = message.data.get('Application')
        apps = self.appmap.get(app_name)
        if apps and len(apps) > 0:
            self.log.info('Launching {}'.format(app_name))
            apps[0].launch()

    @intent_handler(IntentBuilder('CloseDesktopApplicationIntent')
                    .require('CloseKeyword').require('Application'))
    def handle_close_desktop_app(self, message):
        """Close application using killall"""
        app_name = message.data.get("Application")

        if not self.kill_process_by_name(app_name):
            self.log.info(
                "Couldn't kill {} try to get executable from desktop file".format(
                    app_name
                )
            )
            apps = self.appmap.get(app_name)
            if apps:
                app_name = apps[0].get_string("Exec")
                if not self.kill_process_by_name(app_name):
                    self.speak("failed to close {}".format(app_name))

    def kill_process_by_name(self, app_name):
        """Kill a process using the least powerful signal that works."""
        self.log.info("Killing {}".format(app_name))
        for signal in ["SIGINT", "SIGQUIT", "SIGTERM", "SIGKILL"]:
            if subprocess.call(["killall", "-s", signal, app_name]) == 0:
                self.log.info("Killed {} using {}".format(app_name, signal))
                return True

        return False

    @intent_handler(IntentBuilder('LaunchWebsiteIntent')
                    .require('LaunchKeyword').require('Website'))
    def handle_launch_website(self, message):
        """Open a website in the selected webbrowser."""
        site = message.data.get("Website")
        webbrowser.open(IFL_TEMPLATE % (quote(site)))

    @intent_handler(IntentBuilder('SearchWebsiteIntent')
                    .require('SearchKeyword').require('Website')
                    .require('SearchTerms'))
    def handle_search_website(self, message):
        """Open a webbrowser searching for query."""
        site = message.data.get('Website')
        search_terms = message.data.get('SearchTerms')
        search_str = '{} {}'.format(site, search_terms)
        webbrowser.open(IFL_TEMPLATE % (quote(search_str)))


def create_skill():
    return DesktopLauncherSkill()
