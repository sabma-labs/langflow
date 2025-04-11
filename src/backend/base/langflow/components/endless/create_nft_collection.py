import json
from typing import Any
import pdb

from endless_sdk.account import Account
from endless_sdk.endless_tokenv1_client import EndlessTokenV1Client
from endless_sdk.async_client import RestClient

from langflow.custom import Component
from langflow.inputs import SecretStrInput, MessageInput, StrInput
from langflow.io import Output
from langflow.schema import Data


class CreateNFTCollection(Component):
    NODE_URL = "https://rpc-test.endless.link/v1"
    rest_client = RestClient(NODE_URL)
    token_client = EndlessTokenV1Client(rest_client)
    display_name = "Create NFT Collection"
    description = "Create an NFT Collection via API call"
    icon = "images"  # updated icon
    name = "Create NFT Collection"

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

            # Create an account instance with the provided private key.
            account = Account.load_key(self.private_key)
            # Call the asynchronous API to create the collection. This function should be defined
            # elsewhere in your codebase and is expected to return a collection identifier (string)
            collection_info = await self.create_collection(account, self.nft_collection_name,
                                                           self.nft_collection_description, self.nft_collection_uri)

            result = self.output_results(collection_info)
            self.status = result
            print(result)
            return Data(data=result)
        except Exception as e:
            error_result: dict[str, Any] = {"error": str(e)}
            self.status = error_result
            return Data(data=None)

    # The actual API function for creating a collection.
    async def create_collection(
            self, account: Account, name: str, description: str, uri: str
    ) -> str:
        txn_hash = await self.token_client.create_collection(account, name, description, uri)
        await self.rest_client.wait_for_transaction(txn_hash)
        tx_info = await self.rest_client.transaction_by_hash(txn_hash)
        return tx_info

    def output_results(self, data) -> dict:
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
        return {
            "collection_name": collection_name,
            "sender": sender,
            "description": description,
            "uri": uri,
            "royalty_rate": royalty_rate,
            "gas_used": gas_used,
            "status": status
        }
