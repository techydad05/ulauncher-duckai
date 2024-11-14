from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction

from duckduckgo_search import DDGS


class DemoExtension(Extension):

    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        query = event.get_argument() or ""
        model = extension.preferences.get("model") or ""
        wrap_length = int(extension.preferences.get("wrap_length")) or 5
        default_prompt = extension.preferences.get("default_prompt")

        if not query or not model:
            result = ExtensionResultItem(
                icon="images/icon.png",
                name="No question provided",
                description="Please, enter your question",
                on_enter=HideWindowAction()
            )

            return RenderResultListAction([result])

        try:
            ai_answer = DDGS().chat(
                keywords=default_prompt + "\n\n" + query,
                model=model,
                timeout=60
            )
        except Exception as e:
            result = ExtensionResultItem(
                icon="images/icon.png",
                name="An error occurred",
                description=str(e),
            )

            return RenderResultListAction([result])

        wrapped_lines = []
        current_line = ""
        for word in ai_answer.split():
            if len(current_line + word) <= wrap_length:
                current_line += " " + word
            else:
                wrapped_lines.append(current_line.strip())
                current_line = word
        wrapped_lines.append(current_line.strip())

        wrapped_answer = "\n".join(wrapped_lines)

        result = ExtensionResultItem(
            icon="images/icon.png",
            name=model.capitalize(),
            description=wrapped_answer,
            on_enter=CopyToClipboardAction(ai_answer)
        )

        return RenderResultListAction([result])


if __name__ == "__main__":
    DemoExtension().run()