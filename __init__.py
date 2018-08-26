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


import sys
import webbrowser
import subprocess

from adapt.intent import IntentBuilder
from adapt.tools.text.tokenizer import EnglishTokenizer
from os.path import dirname, join

from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
if sys.version_info[0] < 3:
    from urllib import quote
    try:
        import gio
    except ModuleNotFoundError:
        sys.path.append("/usr/lib/python2.7/dist-packages")
        import gio
else:
    from urllib.parse import quote
    from gi.repository import Gio as gio

logger = getLogger(__name__)
__author__ = 'seanfitz'

IFL_TEMPLATE = "http://www.google.com/search?&sourceid=navclient&btnI=I&q=%s"


class DesktopLauncherSkill(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self, "DesktopLauncherSkill")
        self.appmap = {}

    def initialize(self):
        tokenizer = EnglishTokenizer()

        for app in gio.app_info_get_all():
            name = app.get_name().lower()
            entry = [app]
            tokenized_name = tokenizer.tokenize(name)[0]

            if name in self.appmap:
                self.appmap[name] += entry
            else:
                self.appmap[name] = entry

            self.register_vocabulary(name, "Application")
            if name != tokenized_name:
                self.register_vocabulary(tokenized_name, "Application")
                if tokenized_name in self.appmap:
                    self.appmap[tokenized_name] += entry
                else:
                    self.appmap[tokenized_name] = entry

        launch_intent = IntentBuilder(
            "LaunchDesktopApplicationIntent").require("LaunchKeyword").require(
            "Application").build()
        self.register_intent(launch_intent, self.handle_launch_desktop_app)

        close_intent = IntentBuilder(
            "CloseDesktopApplicationIntent").require("CloseKeyword").require(
            "Application").build()
        self.register_intent(close_intent, self.handle_close_desktop_app)

        launch_website_intent = IntentBuilder(
            "LaunchWebsiteIntent").require("LaunchKeyword").require(
            "Website").build()
        self.register_intent(launch_website_intent, self.handle_launch_website)

        search_website = IntentBuilder("SearchWebsiteIntent").require(
            "SearchKeyword").require("Website").require(
            "SearchTerms").build()
        self.register_intent(search_website, self.handle_search_website)

    def handle_launch_desktop_app(self, message):
        app_name = message.data.get('Application')
        apps = self.appmap.get(app_name)
        if apps and len(apps) > 0:
            apps[0].launch()

    def handle_close_desktop_app(self, message):
        app_name = message.data.get('Application')
        subprocess.call( [ "killall", "-9", app_name ] )

    def handle_launch_website(self, message):
        site = message.data.get("Website")
        webbrowser.open(IFL_TEMPLATE % (quote(site)))

    def handle_search_website(self, message):
        site = message.data.get("Website")
        search_terms = message.data.get("SearchTerms")
        search_str = site + " " + search_terms
        webbrowser.open(IFL_TEMPLATE % (quote(search_str)))

    def stop(self):
        pass


def create_skill():
    return DesktopLauncherSkill()
