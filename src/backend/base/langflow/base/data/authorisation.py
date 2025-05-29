import io
import os
import json
import base64
import qrcode
import requests
from dotenv import load_dotenv
from typing import Optional, Sequence, Any, Dict
from fastapi import Depends
from langflow.custom import Component
from langflow.inputs.inputs import DropdownInput, MessageInput, SecretStrInput, InputTypes
from langflow.template.field.base import Output
from langflow.schema.message import Message
from langflow.schema import Data
from sqlmodel import SQLModel, Session, create_engine
from uuid import uuid4
from datetime import datetime, timezone
from langflow.services.database.models.user_input.crud import create_user_input
from sqlmodel import Session
from langflow.services.database.utils import session_getter
from langflow.services.deps import get_db_service, get_settings_service
load_dotenv()
class AuthorizationComponent(Component):
    display_name = "Authorization Method"
    description = "Choose Wallet or Private Key for authorization."

    # Base inputs for both flows
    _base_inputs: list[InputTypes] = [
        DropdownInput(
            name="authorization_method",
            display_name="Authorization Method",
            options=["Wallet", "Private Key"],
            value="Wallet",
            required=True,
            info="Select your authorization method",
            real_time_refresh=True,
        ),
        SecretStrInput(
            name="private_key",
            display_name="Private Key",
            show=False,
            required=False,
            password=True,
            dynamic=True,
            info="Enter your private key if using private-key flow.",

        ),
        MessageInput(
            name="target_user_id",
            display_name="Target User ID",
            dynamic=True,
            show=True,
            required =True,
            info="Existing user ID to link this authorization to.",
            tool_mode=True
        ),
    ]
    inputs = _base_inputs

    outputs = [
        Output(
            name="auth_output",
            display_name="Authorization Result",
            method="perform_wallet_authorization",
        )
    ]

    def update_build_config(self, build_config: Dict[str, Any], field_value: Any, field_name: str | None = None) -> Dict[str, Any]:
        # Hide/require private_key based on dropdown
        if "target_user_id" in build_config:
            build_config["target_user_id"]["show"] = True
            build_config["target_user_id"]["required"] = True
        if "private_key" in build_config:
            build_config["private_key"]["show"] = False
            build_config["private_key"]["required"] = False
        if field_name == "authorization_method" and field_value == "Private Key":
            build_config["private_key"]["show"] = True
            build_config["private_key"]["required"] = True
            build_config["target_user_id"]["show"] = False
            build_config["target_user_id"]["required"] = False
        return build_config

    def generate_qr_code(self, url: str) -> str:
        qr = qrcode.QRCode(border=1)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()

    def _send_qr_to_luffa_app(self, url: str):
        endpoint = os.getenv("LUFFA_ENDPOINT") + "/send"
        headers = {"Content-Type": "application/json"}
        data = {
        "secret": os.getenv("LUFFA_AUTHORIZATION_ROBOT_SECRET_KEY"),
        "uid": self.target_user_id,
        "msg":json.dumps( {"text": url}),
        }

        # 🌟 DEBUG LOGGING
        print("[Luffa ▶] POST", endpoint)
        print("[Luffa ▶] headers:", headers)
        print("[Luffa ▶] payload:", json.dumps(data))

        try:
            response = requests.post(endpoint, headers=headers, json=data, timeout=10)
            print(f"[Reply] Status: {response.status_code}")
            print(f"[Reply] Body:   {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"[Reply] Error:   {e}")

    async def perform_wallet_authorization(
        self,
        user_data: dict,          # FastAPI will inject
    ) -> Data:
        print("USER DATA_________")
        print(user_data)
        async with session_getter(get_db_service()) as session:
            ui = await create_user_input(session, user_data, self.target_user_id)
            if not ui:
                raise RuntimeError("Failed to create UserInput record")
        record_id = ui.id 
        if record_id:
            print(f"Inserted row with id={record_id}")    
        url = f"{os.getenv('WALLET_AUTHORIZATION_ENDPOINT')}?id={record_id}"
        qr_b64 = self.generate_qr_code(url)
        self._send_qr_to_luffa_app(url)
        return Data(data={
            "record_id": record_id,
            "authorization_url": url,
            "qr_code_image": "data:image/png;base64,"+qr_b64,
        })
