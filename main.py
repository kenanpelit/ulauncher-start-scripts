import logging
import os
from pathlib import Path
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import (
    KeywordQueryEvent,
    PreferencesEvent,
    PreferencesUpdateEvent
)
from ulauncher.api.shared.item.ExtensionSmallResultItem import ExtensionSmallResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction

logger = logging.getLogger(__name__)

DEFAULT_ICON = "images/icon.svg"
SCRIPTS_PATH = "/etc/profiles/per-user/kenan/bin"

def search_start_scripts(search_term=""):
    """Search for scripts starting with 'start-' in the scripts directory"""
    scripts_dir = Path(SCRIPTS_PATH)
    if not scripts_dir.exists():
        raise FileNotFoundError(f'Scripts directory not found: {SCRIPTS_PATH}')

    scripts = []
    for script in scripts_dir.glob("start-*"):
        if script.is_file() and os.access(script, os.X_OK):
            if search_term.lower() in script.name.lower():
                scripts.append(script)

    return sorted(scripts)

class StartScriptsExtension(Extension):
    def __init__(self):
        super(StartScriptsExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent, PreferencesEventListener())

class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        items = []
        query = event.get_argument() or ""

        try:
            scripts = search_start_scripts(query)
        except FileNotFoundError as e:
            logger.error(e)
            items.append(ExtensionSmallResultItem(
                icon=DEFAULT_ICON,
                name='Scripts directory not found'
            ))
            return RenderResultListAction(items)

        if not scripts:
            items.append(ExtensionSmallResultItem(
                icon=DEFAULT_ICON,
                name='No matching scripts found'
            ))
            return RenderResultListAction(items)

        for script in scripts[:20]:
            items.append(ExtensionSmallResultItem(
                icon=DEFAULT_ICON,
                name=script.name,
                on_enter=RunScriptAction(str(script))
            ))

        return RenderResultListAction(items)

class PreferencesEventListener(EventListener):
    def on_event(self, event, extension):
        extension.keyword = event.preferences["kw"]

if __name__ == '__main__':
    StartScriptsExtension().run()

