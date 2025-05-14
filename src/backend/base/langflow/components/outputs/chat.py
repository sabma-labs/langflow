import re 
from collections.abc import Generator
from typing import Any

from langflow.base.io.chat import ChatComponent
from langflow.inputs import BoolInput
from langflow.inputs.inputs import HandleInput
from langflow.io import DropdownInput, MessageTextInput, Output
from langflow.schema.data import Data
from langflow.schema.dataframe import DataFrame
from langflow.schema.message import Message
from langflow.schema.properties import Source
from langflow.schema.content_types import MediaContent
from langflow.utils.constants import (
    MESSAGE_SENDER_AI,
    MESSAGE_SENDER_NAME_AI,
    MESSAGE_SENDER_USER,
)

class ChatOutput(ChatComponent):
    display_name = "Chat Output"
    description = "Display a chat message in the Playground. Supports base64 images."
    icon = "MessagesSquare"
    name = "ChatOutput"
    minimized = True
    BASE64_REGEX = re.compile(
        r"^(?:[A-Za-z0-9+/]{4})*"
        r"(?:[A-Za-z0-9+/]{2}==|"
        r"[A-Za-z0-9+/]{3}=)?$"
    )

    inputs = [
        HandleInput(
            name="input_value",
            display_name="Text or Base64 Image",
            info="Message or base64 image data to be passed as output.",
            input_types=["Data", "DataFrame", "Message", "str"],
            required=True,
        ),
        BoolInput(
            name="should_store_message",
            display_name="Store Messages",
            info="Store the message in the history.",
            value=True,
            advanced=True,
        ),
        DropdownInput(
            name="sender",
            display_name="Sender Type",
            options=[MESSAGE_SENDER_AI, MESSAGE_SENDER_USER],
            value=MESSAGE_SENDER_AI,
            advanced=True,
            info="Type of sender.",
        ),
        MessageTextInput(
            name="sender_name",
            display_name="Sender Name",
            info="Name of the sender.",
            value=MESSAGE_SENDER_NAME_AI,
            advanced=True,
        ),
        MessageTextInput(
            name="session_id",
            display_name="Session ID",
            info="The session ID of the chat. If empty, the current session ID parameter will be used.",
            advanced=True,
        ),
        MessageTextInput(
            name="data_template",
            display_name="Data Template",
            value="{text}",
            advanced=True,
            info="Template to convert Data to Text. If left empty, it will be dynamically set to the Data's text key.",
        ),
        MessageTextInput(
            name="background_color",
            display_name="Background Color",
            info="The background color of the icon.",
            advanced=True,
        ),
        MessageTextInput(
            name="chat_icon",
            display_name="Icon",
            info="The icon of the message.",
            advanced=True,
        ),
        MessageTextInput(
            name="text_color",
            display_name="Text Color",
            info="The text color of the name",
            advanced=True,
        ),
        BoolInput(
            name="clean_data",
            display_name="Basic Clean Data",
            value=True,
            info="Whether to clean the data",
            advanced=True,
        ),
    ]

    outputs = [
        Output(
            display_name="Message",
            name="message",
            method="message_response",
        ),
    ]

    IMAGE_PREFIXES = (
        "data:image/png;base64,", 
        "data:image/jpeg;base64,", 
        "data:image/gif;base64,"
    )

    def _build_source(self, id_: str | None, display_name: str | None, source: str | None) -> Source:
        print(f"[DEBUG] Building source with id: {id_}, display_name: {display_name}, source: {source}")
        source_dict = {}
        if id_:
            source_dict["id"] = id_
        if display_name:
            source_dict["display_name"] = display_name
        if source:
            if hasattr(source, "model_name"):
                source_dict["source"] = source.model_name
            elif hasattr(source, "model"):
                source_dict["source"] = str(source.model)
            else:
                source_dict["source"] = str(source)
        print(f"[DEBUG] Final source_dict: {source_dict}")
        return Source(**source_dict)

    async def message_response(self) -> Message:
        print("[DEBUG] Starting message_response...")
        print(self.input_value)
        # print(f"[DEBUG] Raw input_value: {self.input_value}")

        # if isinstance(self.input_value, Message):
        #     print("[DEBUG] Input is of type Message")
        #     message = self.input_value

        #     for block in getattr(message, "content_blocks", []) or []:
        #         if block.title == "Agent Steps":
        #             for piece in block.contents:
        #                 if getattr(piece, "type", "") == "tool_use":
        #                     uri = getattr(piece, "output", "")
        #                     if isinstance(uri, str) and uri.startswith("data:image/"): 
        #                         print("I am in block")                               
        #                         message.set_text(uri)
        #                         print(message.get_text())
                                

        # First convert the input to string if needed
        text = self.convert_to_string()
        # Get source properties
        source, icon, display_name, source_id = self.get_properties_from_source_component()
        background_color = self.background_color
        text_color = self.text_color
        if self.chat_icon:
            icon = self.chat_icon

        # Create or use existing Message object
        if isinstance(self.input_value, Message):
            message = self.input_value
            # Update message properties
            message.text = text
        else:
            message = Message(text=text)
        source, icon, display_name, source_id = self.get_properties_from_source_component()
        background_color = self.background_color
        text_color = self.text_color
        if self.chat_icon:
            icon = self.chat_icon

        message.sender = self.sender
        message.sender_name = self.sender_name
        message.session_id = self.session_id
        message.flow_id = getattr(self, 'graph', None) and self.graph.flow_id
        message.properties.source = self._build_source(source_id, display_name, source)
        message.properties.icon = icon
        message.properties.background_color = background_color
        message.properties.text_color = text_color

        if self.session_id and self.should_store_message:
            print("[DEBUG] Storing message in session...")
            stored = await self.send_message(message)
            self.message.value = stored
            message = stored
        else:
            print("[DEBUG] Not storing message (session_id or flag missing).")

        self.status = message
        print("[DEBUG] Returning final message object.")
        return message

    def _validate_input(self) -> None:
        print("[DEBUG] Validating input type...")
        if self.input_value is None:
            raise ValueError("Input data cannot be None")
        if isinstance(self.input_value, list) and not all(
            isinstance(item, (Message, Data, DataFrame, str)) for item in self.input_value
        ):
            invalid = [type(item).__name__ for item in self.input_value if not isinstance(item, (Message, Data, DataFrame, str))]
            raise TypeError(f"Expected Data, DataFrame, Message, or str, got {invalid}")
        if not isinstance(self.input_value, (Message, Data, DataFrame, str, list, Generator, type(None))):
            raise TypeError(f"Unexpected input type: {type(self.input_value).__name__}")
        print("[DEBUG] Input validation passed.")

    def _safe_convert(self, data: Any) -> str:
        print(f"[DEBUG] Converting data: {data}")
        try:
            if isinstance(data, str):
                return data
            if isinstance(data, Message):
                return data.get_text()
            if isinstance(data, Data):
                if data.get_text() is None:
                    raise ValueError("Empty Data object")
                return data.get_text()
            if isinstance(data, DataFrame):
                if self.clean_data:
                    data = data.dropna(how="all")
                    data = data.replace(r"^\s*$", "", regex=True)
                    data = data.replace(r"\n+", "\n", regex=True)
                df = data.replace(r"\|", r"\\|", regex=True)
                df = df.map(lambda x: str(x).replace("\n", "<br/>") if isinstance(x, str) else x)
                return df.to_markdown(index=False)
            return str(data)
        except Exception as e:
            print(f"[ERROR] Failed to convert data: {e}")
            raise ValueError(f"Error converting data: {e}") from e

    def convert_to_string(self) -> str | Generator[Any, None, None]:
        print("[DEBUG] Starting convert_to_string...")
        self._validate_input()
        # if isinstance(self.input_value, Message):
        #     print("[DEBUG] Input is Message for conversion")
        #     for block in getattr(self.input_value, "content_blocks", []) or self.input_value.data.get("content_blocks", []):
        #         for piece in block.contents:
        #             output = getattr(piece, "output", None) or piece.get("output")
        #             if isinstance(output, str) and self.BASE64_REGEX.fullmatch(output):
        #                 print("[DEBUG] Found base64 image in Message content_blocks")
        #                 return output
        if isinstance(self.input_value, list):
            return "\n".join([self._safe_convert(item) for item in self.input_value])
        if isinstance(self.input_value, Generator):
            return self.input_value
        return self._safe_convert(self.input_value)
