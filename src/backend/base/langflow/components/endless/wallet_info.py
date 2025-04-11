import json
import requests

from langflow.custom import Component
from langflow.inputs import DropdownInput, MultilineInput, SecretStrInput, StrInput, MessageInput, DataInput
from langflow.io import Output
from langflow.schema import Data
from endless_sdk.async_client import RestClient
from endless_sdk.account import Account
import asyncio

class EndlessWalletInfoComponent(Component):
    display_name = "Endless Wallet Info"
    description = "Endless Wallet Info"
    icon = "wallet"
    name = "EndlessWalletInfo"
    # legacy = True

    inputs = [
        DataInput(
            name="nft_collection_name",
            display_name="Collection Name",
            info="Enter the name of the NFT collection",
            required=True,
            value=""
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
        # print(self.nft_collection_name)

        rest_client = RestClient("https://rpc-test.endless.link/v1")
        # faucet_client = FaucetClient(
        #     FAUCET_URL, rest_client, FAUCET_AUTH_TOKEN
        # )  # <:!:section_1

        alice = Account.load_key("0x68e7f9a75606e0baa3c2487b32ba016ead6d8d71a220f5a69a8b7645468c54df")

        print("\n=== Addresses ===")
        print(f"Alice: {alice.address()}")

        alice_balance = rest_client.account_balance(alice.address())
        [alice_balance] = await asyncio.gather(*[alice_balance])
        print(f"Alice: {alice_balance}")

        return Data(data=None)