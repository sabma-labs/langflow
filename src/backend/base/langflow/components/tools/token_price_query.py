import requests
from langflow.custom import Component
from langflow.inputs import StrInput
from langflow.template import Output
from langflow.schema.message import Message

class TokenPriceComponent(Component):
    display_name = "Token Price Query"
    description = (
        "Queries the current USD price of a specified token using the CoinGecko API."
    )
    icon = "price-tag"
    name = "TokenPriceComponent"

    # Define a single string input for the token ID.
    inputs = [
        StrInput(
            name="token_id",
            display_name="Token ID",
            value="bitcoin",
            info="The token ID as recognized by CoinGecko (e.g., 'bitcoin', 'ethereum').",
            tool_mode=True,
        ),
    ]

    # Define the output method that returns the price as a Message.
    outputs = [
        Output(display_name="Price Output", name="price_output", method="query_token_price"),
    ]

    def query_token_price(self) -> Message:
        # Build the URL to query the token price from CoinGecko.
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={self.token_id}&vs_currencies=usd"
        try:
            response = requests.get(url)
            data = response.json()
            price = data.get(self.token_id, {}).get("usd")
            if price is not None:
                output_text = f"The current price of {self.token_id} is ${price:.2f} USD."
            else:
                output_text = f"Price for '{self.token_id}' not found."
        except Exception as e:
            output_text = f"Error querying token price: {str(e)}"
        return Message(text=output_text)
