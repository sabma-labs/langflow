import base64
import imghdr
import requests
from urllib.parse import urlparse
from typing import Any
from endless_sdk.account import Account
from endless_sdk.endless_tokenv1_client import EndlessTokenV1Client
from endless_sdk.async_client import RestClient
from langflow.custom import Component
from langflow.inputs import  SecretStrInput, MessageInput , StrInput
from langflow.io import Output
from langflow.schema import Data
from endless_sdk.api_config import APIConfig , NetworkType

class MintNFT(Component):
    config_type = NetworkType.TESTNET
    api_config = APIConfig(config_type)
    rest_client = RestClient(api_config.NODE_URL,api_config.INDEXER_URL)
    token_client = EndlessTokenV1Client(rest_client)
    token_client = EndlessTokenV1Client(rest_client)
    display_name = "Mint NFT"
    description = "Mint a NFT Token via API call"
    icon = "Globe"  # updated icon
    name = "Mint NFT"
    
    # Adjust inputs to collect information needed for creating the NFT collection.
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
    ]

    outputs = [
        Output(
            display_name="NFT Response",
            name="Mint NFT",
            method="mint_nft"
        ),
    ]
    
    

    async def mint_nft(self) -> Data:
        try:
            
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
            self.status = result
            print(result)
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
    
   



    def process_nft_input(nft_input):
        """
        Processes the input which can be either a text URI or image data (bytes).
        
        - If the input is a string, it is assumed to be a text URI and returned directly.
        - If the input is bytes, it is assumed to be image data. The function uses imghdr
        to detect the image type, encodes the image in Base64, and returns a data URI.
        
        Parameters:
            nft_input (str or bytes): Either a text URI or raw image data.
            
        Returns:
            str: A text URI if the input was a string, or a Base64 data URI if the input was image data.
        """
        # Check if the input is a text URI.
        if isinstance(nft_input, str):
            return nft_input
        
        # If the input is bytes, determine if it's valid image data.
        elif isinstance(nft_input, bytes):
            # Determine the image type from the raw data.
            image_type = imghdr.what(None, h=nft_input)
            if image_type:
                # Convert the image data to a Base64 string.
                base64_data = base64.b64encode(nft_input).decode('utf-8')
                # Construct the data URI.
                data_uri = f"data:image/{image_type};base64,{base64_data}"
                return data_uri
            else:
                raise ValueError("The provided byte data is not recognized as valid image data.")
        
        else:
            raise ValueError("Unsupported input type. Provide either a text URI (str) or image data (bytes).")

    