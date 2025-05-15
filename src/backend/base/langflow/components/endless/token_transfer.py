import asyncio
import json

from langflow.custom import Component
from langflow.inputs import FloatInput, MessageInput, SecretStrInput
from langflow.io import Output
from langflow.schema import Data


class TokenTransfer(Component):
    display_name = "Token Transfer"
    description = "Transfer tokens using Endless TypeScript SDK via Node.js script"
    icon = "send"
    name = "TokenTransfer"

    inputs = [
        SecretStrInput(
            name="private_key",
            display_name="Sender Private Key",
            required=True,
        ),
        MessageInput(
            name="recipient_address",
            display_name="Recipient Address",
            required=True,
        ),
        FloatInput(
            name="amount",
            display_name="Amount",
            required=True,
        ),
        MessageInput(
            name="token_type",
            display_name="Token Type",
            info="e.g. 0x4::mytoken::MYTOKEN",
            required=True,
        ),
    ]

    outputs = [
        Output(display_name="Transfer Result", name="result", method="transfer_token"),
    ]

    async def transfer_token(self) -> Data:
        try:
            process = await asyncio.create_subprocess_exec(
                "node",
                "token_transfer.ts",
                self.private_key,
                self.recipient_address,
                str(int(self.amount)),
                self.token_type,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
            except asyncio.TimeoutError:
                process.kill()
                await process.communicate()
                return Data(data={"error": "Token transfer timed out"})

            if process.returncode != 0:
                try:
                    error_data = json.loads(stderr.decode())
                    return Data(data={"error": error_data.get("error", "Unknown error")})
                except json.JSONDecodeError:
                    return Data(data={"error": stderr.decode()})

            data = json.loads(stdout.decode())
            return Data(data=data)

        except Exception as e:  # noqa: BLE001 - catching to report runtime errors to frontend
            return Data(data={"error": str(e)})
