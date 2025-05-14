import json
from typing import Any
import pdb

from endless_sdk.account import Account
from endless_sdk.endless_tokenv1_client import EndlessTokenV1Client
from endless_sdk.async_client import RestClient
from endless_sdk.api_config import APIConfig, NetworkType
from langflow.custom import Component
from langflow.inputs import SecretStrInput, MessageInput
from langflow.io import Output
from langflow.schema import Data

class CreateNFTCollection(Component):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_type = NetworkType.TESTNET
        self.api_config = APIConfig(self.config_type)
        self.rest_client = RestClient(self.api_config.NODE_URL, self.api_config.INDEXER_URL)
        self.token_client = EndlessTokenV1Client(self.rest_client)


    display_name = "Create NFT Collection"
    description = "Create an NFT Collection via API call"
    icon = "Globe"
    name = "Create NFT Collection"
    
    inputs = [
        SecretStrInput(
            name="private_key",
            display_name="Private Key",
            info="Your API private key",
            advanced=False,
            value="api_key",
            required=True,
        ),
        MessageInput(
            name="nft_collection_name",
            display_name="Collection Name",
            info="Enter the name of the NFT collection",
            required=True,
            tool_mode=True,
            value=""
        ),
        MessageInput(
            name="nft_collection_description",
            display_name="Description",
            info="Enter a description for the NFT collection",
            required=True,
            tool_mode=True,
            value=""
        ),
        MessageInput(
            name="nft_collection_uri",
            display_name="URI",
            info="Enter the URI for the NFT collection metadata",
            required=True,
            tool_mode=True,
            value=""
        ),
    ]

    outputs = [
        Output(
            display_name="Collection Response",
            name="collection",
            method="create_nft_collection"
        ),
    ]
    
    async def create_nft_collection(self) -> Data:
        try:
            print("[DEBUG] Starting create_nft_collection")
            print(f"[DEBUG] Inputs - PrivateKey: {self.private_key[:5]}..., Name: {self.nft_collection_name}, Desc: {self.nft_collection_description}, URI: {self.nft_collection_uri}")
            account = Account.load_key(self.private_key)
            print("[DEBUG] Account loaded successfully")

            pdb.set_trace()  # Debugging breakpoint

            collection_info = await self.create_collection(
                account, 
                self.nft_collection_name, 
                self.nft_collection_description, 
                self.nft_collection_uri
            )

            print(f"[DEBUG] Collection info received: {json.dumps(collection_info, indent=2)}")

            result = self.output_results(collection_info)
            print(f"[DEBUG] Formatted output result: {result}")

            self.status = result
            return Data(data=result)
        except Exception as e:
            print(f"[ERROR] Exception occurred: {e}")
            error_result: dict[str, Any] = {"error": str(e)}
            self.status = error_result
            return Data(data=error_result)

    async def create_collection(
        self, account: Account, name: str, description: str, uri: str
    ) -> str:
        print(f"[DEBUG] Creating collection with name: {name}, description: {description}, uri: {uri}")
        txn_hash = await self.token_client.create_collection(account, name, description, uri)
        print(f"[DEBUG] Transaction hash received: {txn_hash}")

        await self.rest_client.wait_for_transaction(txn_hash)
        print(f"[DEBUG] Transaction {txn_hash} confirmed.")

        tx_info = await self.rest_client.transaction_by_hash(txn_hash)
        print(f"[DEBUG] Transaction info: {json.dumps(tx_info, indent=2)}")
        return tx_info

    def output_results(self, data) -> dict:
        print(f"[DEBUG] Processing output results from transaction data")

        collection_name = ""
        description = ""
        uri = ""
        royalty_rate = ""

        for change in data["collection_id"]["changes"]:
            change_data = change.get("data", {})
            change_type = change_data.get("type", "")
            print(f"[DEBUG] Processing change type: {change_type}")

            if change_type == "0x4::collection::Collection":
                collection_details = change_data.get("data", {})
                collection_name = collection_details.get("name", "")
                description = collection_details.get("description", "")
                uri = collection_details.get("uri", "")
                print(f"[DEBUG] Collection details - Name: {collection_name}, Desc: {description}, URI: {uri}")
            
            if change_type == "0x4::royalty::Royalty":
                royalty_details = change_data.get("data", {})
                numerator = royalty_details.get("numerator", "")
                denominator = royalty_details.get("denominator", "")
                royalty_rate = f"{numerator}/{denominator}"
                print(f"[DEBUG] Royalty details - Rate: {royalty_rate}")

        sender = data["collection_id"].get("sender", "")
        gas_used = data["collection_id"].get("gas_used", "")
        status = data["collection_id"].get("vm_status", "")

        result = {
            "collection_name": collection_name,
            "sender": sender,
            "description": description,
            "uri": uri,
            "royalty_rate": royalty_rate,
            "gas_used": gas_used,
            "status": status
        }

        print(f"[DEBUG] Final output result: {result}")
        return result
