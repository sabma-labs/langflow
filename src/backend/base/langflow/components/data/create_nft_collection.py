import os 
from typing import Any, Dict
from endless_sdk.account import Account
from endless_sdk.endless_tokenv1_client import EndlessTokenV1Client
from endless_sdk.async_client import RestClient
from endless_sdk.api_config import APIConfig, NetworkType
from langflow.custom import Component
from langflow.inputs import SecretStrInput, MessageInput, BoolInput
from langflow.io import Output
from langflow.schema import Data
from langflow.base.data.authorisation import AuthorizationComponent
from fastapi import Depends
from sqlmodel import SQLModel, Session, create_engine
from dotenv import load_dotenv
load_dotenv()
class CreateNFTCollection(AuthorizationComponent):
    display_name = "Create NFT Collection"
    description = "Create an NFT Collection via API call"
    icon = "Globe"
    name = "Create NFT Collection"

    def __init__(self, **data: Any):
        super().__init__(**data)
        # Setup chain clients
        self.config_type = NetworkType.TESTNET
        self.api_config = APIConfig(self.config_type)
        self.rest_client = RestClient(self.api_config.NODE_URL, self.api_config.INDEXER_URL)
        self.token_client = EndlessTokenV1Client(self.rest_client)

    # Re-use the same auth inputs PLUS these three:
    inputs = [
        *AuthorizationComponent._base_inputs,
        MessageInput(
            name="nft_collection_name",
            display_name="Collection Name",
            required=True,
            info="Name of the NFT collection.",
            tool_mode=True
        ),
        MessageInput(
            name="nft_collection_description",
            display_name="Description",
            required=True,
            info="Description for the NFT collection.",
            tool_mode=True
        ),
        MessageInput(
            name="nft_collection_uri",
            display_name="URI",
            required=True,
            info="Metadata URI for the collection.",
            tool_mode=True
        ),
        BoolInput(
            name="return_direct",
            display_name="Return Direct",
            info="Return the result directly from the Tool.",
            advanced=True,
            value=True
        ),
    ]

    outputs = [
        Output(
            display_name="Collection Response",
            name="collection",
            method="create_nft_collection",
        ),
    ]
    
    def update_build_config(self, build_config, field_value, field_name=None):
        # First let the base class handle standard inputs
        build_config = super().update_build_config(build_config, field_value, field_name)
        # Now wire up our direct-return flag
        if field_name == "return_direct":
            build_config["return_direct"] = bool(field_value)
        return build_config
                                     
    
    
    async def create_nft_collection(self, db: Session = Depends()) -> Data:
        user_data = {
            "function": "create_nft_collection",
            "nft_collection_name": f"{self.nft_collection_name}",
            "nft_collection_description": f"{self.nft_collection_description}",
            "nft_collection_uri": f"{self.nft_collection_uri}",
            "target_user": f"{self.target_user_id}"
        }
        if self.authorization_method == "Wallet":
                return  await self.perform_wallet_authorization(user_data=user_data)
        # 2) Private-key flow
        if not self.private_key:
            raise ValueError("Private Key must be provided in Private Key mode.")
        account = Account.load_key(self.private_key)
        txn = await self._create_collection_on_chain(
            account,
            self.nft_collection_name,
            self.nft_collection_description,
            self.nft_collection_uri,
        )
        result = self._parse_transaction(txn)
        # private-key mode: just return the parsed result
        return Data(data=result)
    
    async def _create_collection_on_chain(self, account, name: str, description: str, uri: str) -> Dict:
        txn_hash = await self.token_client.create_collection(account, name, description, uri)
        await self.rest_client.wait_for_transaction(txn_hash)
        return await self.rest_client.transaction_by_hash(txn_hash)

    def _parse_transaction(self, data: Dict) -> Dict[str, Any]:
        # Extract collection info, royalty, gas, status
        details = {
            "collection_name": "",
            "description": "",
            "uri": "",
            "royalty_rate": "",
            "sender": data.get("collection_id", {}).get("sender", ""),
            "gas_used": data.get("collection_id", {}).get("gas_used", ""),
            "status": data.get("collection_id", {}).get("vm_status", ""),
        }
        for change in data.get("collection_id", {}).get("changes", []):
            c = change.get("data", {})
            if c.get("type") == "0x4::collection::Collection":
                d = c.get("data", {})
                details.update({
                    "collection_name": d.get("name", ""),
                    "description": d.get("description", ""),
                    "uri": d.get("uri", ""),
                })
            if c.get("type") == "0x4::royalty::Royalty":
                r = c.get("data", {})
                details["royalty_rate"] = f"{r.get('numerator','')}/{r.get('denominator','')}"
        return details
