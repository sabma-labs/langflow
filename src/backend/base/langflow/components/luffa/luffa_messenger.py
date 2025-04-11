import json
import requests

from langflow.custom import Component
from langflow.inputs import DropdownInput, MultilineInput, SecretStrInput, StrInput, MessageInput
from langflow.io import Output
from langflow.schema import Data

class LuffaMessengerComponent(Component):
    display_name = "Luffa Messenger"
    description = "Send Luffa messages"
    icon = "message-square-reply"
    name = "LuffaMessenger"
    # legacy = True

    inputs = [
        SecretStrInput(
            name="secret",
            display_name="Luffa bot secret",
            info="The secret of the bot that will be used",
            advanced=False,
            value="SECRET",
            required=True,
        ),
        DropdownInput(
            name="target_type",
            display_name="Target Type",
            options=["User", "Group"],
            info="Select whether the target is a user or a group.",
            real_time_refresh=True,
            advanced=False,
            tool_mode=True,
        ),
        StrInput(
            name="target_id",
            display_name="Target ID",
            info="Enter the user ID or group ID of the message recipient.",
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
            tool_mode=True,
        ),
    ]

    outputs=[
        Output(display_name="Data", name="data", method="send_handler"),
    ]

    endpoint = "https://apibot.luffa.im/robot"

    async def send_handler(self) -> Data:
        if self.target_type == "Group":
            url = f"{self.endpoint}/sendGroup"
        else:
            url = f"{self.endpoint}/send"

        headers = {"Content-Type": "application/json"}
        data = {
            "secret": self.secret,
            "uid": self.target_id,
            "msg": json.dumps({ "text": self.message }),
        }

        print(self.endpoint)
        print(self.target_id)
        print(self.message)
        print(f"url: {url}, target_id: {self.target_id}, message: {self.message}")

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