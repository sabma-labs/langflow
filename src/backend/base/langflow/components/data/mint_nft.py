import base64
import imghdr
import requests
from urllib.parse import urlparse
from typing import Any
from endless_sdk.account import Account
from endless_sdk.endless_tokenv1_client import EndlessTokenV1Client
from endless_sdk.async_client import RestClient
from langflow.inputs import MessageInput, BoolInput
from langflow.io import Output
from langflow.schema import Data
from endless_sdk.api_config import APIConfig , NetworkType
from langflow.base.data.authorisation import AuthorizationComponent
from dotenv import load_dotenv
load_dotenv()
class MintNFT(AuthorizationComponent):
    display_name = "Mint NFT"
    description = "Mint a NFT Token via API call"
    icon = "Globe"  # updated icon
    name = "Mint NFT"

    def __init__(self, **data: Any):
        super().__init__(**data)
        # Setup chain clients
        self.config_type = NetworkType.TESTNET
        self.api_config = APIConfig(self.config_type)
        self.rest_client = RestClient(self.api_config.NODE_URL, self.api_config.INDEXER_URL)
        self.token_client = EndlessTokenV1Client(self.rest_client)
    
    # Adjust inputs to collect information needed for creating the NFT collection.
    inputs = [
        *AuthorizationComponent._base_inputs,
        MessageInput(
            name="nft_collection_name",
            display_name="Collection Name",
            info="Enter the name of the NFT collection",
            required=True,
            tool_mode=True,
            value = ""
        ),
        MessageInput(
            name="nft_name",
            display_name="NFT Name",
            info="Enter a Name for the NFT",
            required=True,
            tool_mode=True,
            value = ""
        ),
        MessageInput(
            name="nft_description",
            display_name="Description",
            info="Enter a description for the NFT",
            required=True,
            tool_mode=True,
            value = ""
        ),
        MessageInput(
            name="nft_uri",
            display_name="URI",
            info="Enter the URI for the NFT",
            required=True,
            tool_mode=True,
            value = ""
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
            display_name="NFT Response",
            name="Mint NFT",
            method="mint_nft"
        ),
    ]


    def update_build_config(self, build_config, field_value, field_name=None):
        # First let the base class handle standard inputs
        build_config = super().update_build_config(build_config, field_value, field_name)
        # Now wire up our direct-return flag
        if field_name == "return_direct":
            build_config["return_direct"] = bool(field_value)
        return build_config
    
    

    async def mint_nft(self) -> Data:
        try:
            user_data = {
            "function": "mint_nft",
            "nft_collection_name": f"{self.nft_collection_name}",
            "nft_description": f"{self.nft_description}",
            "nft_uri": f"{self.nft_uri}",
            "nft_name": f"{self.nft_name}",
            }
            # 1) If Wallet flow: hand off to parent
            if self.authorization_method == "Wallet":
                return  await self.perform_wallet_authorization(user_data=user_data)
                
            # 2) Private-key flow
            if not self.private_key:
                raise ValueError("Private Key must be provided in Private Key mode.")
            
            # Create an account instance with the provided private key.
            account = Account.load_key(self.private_key)
            # Call the asynchronous API to create the collection. This function should be defined
            # elsewhere in your codebase and is expected to return a collection identifier (string)
            nft_info = await self.mint_nft_api(account, 
                                                    self.nft_collection_name,
                                                    self.nft_name, 
                                                    self.nft_description, 
                                                    self.nft_uri
                                                    )
            
            
            result = self.output_results(nft_info)
            return Data(data=result)
        except Exception as e:
            error_result: dict[str, Any] = {"error": str(e)}
            self.status = error_result
            return Data(data=None)

    # The actual API function for creating a collection.
    async def mint_nft_api(
        self, account: Account, collection_name: str,nft_name: str, description: str, uri: str
    ) -> str:
        txn_hash = await self.token_client.create_token(account,collection_name,nft_name,description,uri)
        await self.rest_client.wait_for_transaction(txn_hash)
        tx_info = await self.rest_client.transaction_by_hash(txn_hash)
        return tx_info
    
    def output_results(self,data) -> dict:
                # Initialize variables with default empty values in case the change records are missing
        collection_name = ""
        description = ""
        uri = ""
        royalty_rate = ""

        # Extract the collection info and royalty information from the changes list.
        for change in data["collection_id"]["changes"]:
            change_data = change.get("data", {})
            change_type = change_data.get("type", "")
            
            # Extract collection details
            if change_type == "0x4::collection::Collection":
                collection_details = change_data.get("data", {})
                collection_name = collection_details.get("name", "")
                description = collection_details.get("description", "")
                uri = collection_details.get("uri", "")
                
            # Extract royalty information
            if change_type == "0x4::royalty::Royalty":
                royalty_details = change_data.get("data", {})
                numerator = royalty_details.get("numerator", "")
                denominator = royalty_details.get("denominator", "")
                royalty_rate = f"{numerator}/{denominator}"

        # Gather other top-level values.
        sender = data["collection_id"].get("sender", "")
        gas_used = data["collection_id"].get("gas_used", "")
        status = data["collection_id"].get("vm_status", "")

        # Build the result dictionary.
        return  {
            "collection_name": collection_name,
            "sender": sender,
            "description": description,
            "uri": uri,
            "royalty_rate": royalty_rate,
            "gas_used": gas_used,
            "status": status
        }
    
   
