import json
import requests

from langflow.custom import Component
from langflow.inputs import DropdownInput, MultilineInput, SecretStrInput, StrInput, MessageInput
from langflow.io import Output
from langflow.schema import Data

class TelegramMessengerComponent(Component):
    display_name = "Telegram Messenger"
    description = "Send Telegram messages"
    icon = "check-check"
    name = "TelegramMessenger"
    # legacy = True

    inputs = [
        SecretStrInput(
            name="token",
            display_name="Telegram bot token",
            info="The token of the bot that will be used",
            advanced=False,
            value="",
            required=True,
        ),
        MessageInput(
            name="chat_id",
            display_name="Chat ID",
            info="Enter the chat id of the message recipient.",
            value="",
            tool_mode=True,
            advanced=False,
        ),
        MultilineInput(
            name="message",
            display_name="Message",
            info="Message text",
            value="",
            advanced=False,
        ),
    ]

    outputs=[
        Output(display_name="Data", name="data", method="send_handler"),
    ]

    async def send_handler(self) -> Data:
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"

        headers = {"Content-Type": "application/json"}
        data = {
            "chat_id": self.chat_id,
            "text": self.message,
        }

        print(self.chat_id)
        print(self.message)
        print(f"url: {url}, target_id: {self.chat_id}, message: {self.message}")

        try:
            response = requests.post(url, headers=headers, json=data)
            print(f"[Reply] Status: {response.status_code}")
            if response.status_code == 200:
                print(f"[Reply] Response: {response.json()}")
                return Data(data=response.json())
            else:
                print(f"[Reply] Failed. Status: {response.status_code}, Content: {response.content}")
                return Data(data=json.loads(response.content.decode("utf-8", errors="replace")))
        except requests.exceptions.RequestException as e:
            print(f"[Reply] Error: {e}")
            return Data(data=None)