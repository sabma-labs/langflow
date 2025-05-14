import asyncio
from typing import Any, Callable
from functools import lru_cache
import re
from aiohttp import ClientResponseError
import aiohttp
from PIL import Image, ImageDraw
import asyncio
from aiohttp import ClientSession, ClientTimeout
from functools import lru_cache
from langflow.io import Output  
from tenacity import retry, stop_after_attempt, wait_fixed
from langflow.schema.message import Message
from langflow.custom import Component
from langflow.schema.content_block import ContentBlock
from langflow.schema.content_types import MediaContent
from langflow.field_typing import LanguageModel
from langflow.io import (
    FloatInput,
    IntInput,
    MessageInput,
)

class StableDiffusionComponent(Component):
    display_name = "Stable Diffusion (Text→Image)"
    description = "Generate images from prompts via Hugging Face Inference API or local fallback."
    icon = "Image"
    name = "StableDiffusion"
    return_direct = True
    api_base = "https://82e9-131-227-23-35.ngrok-free.app"
    api_path = "/generate_url"

    inputs = [
        MessageInput(
            name="input_value",
            display_name="Prompt",
            required=True,
            tool_mode=True,
        ),
        IntInput(name="width", display_name="Width", value=512, tool_mode=True),
        IntInput(name="height", display_name="Height", value=512, tool_mode=True),
        IntInput(name="num_inference_steps", display_name="Steps", value=50, tool_mode=True),
        FloatInput(name="guidance_scale", display_name="Guidance", value=7.5, tool_mode=True),
    ]
    
    outputs = [
        Output(
            display_name="Generate Image",
            name="Generate Image",
            method="generate",
        ),
    ]


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._session: ClientSession | None = None
        # one-time timeout config
        self._timeout = ClientTimeout(total=30)

    async def _get_session(self) -> ClientSession:
        if self._session is None or self._session.closed:
            self._session = ClientSession(timeout=self._timeout)
        return self._session
    
    async def __aexit__(self, exc_type, exc, tb):
        if self._session and not self._session.closed:
            await self._session.close()

    async def _call_api(self, prompt: str, width: int, height: int,
                    num_inference_steps: int, guidance_scale: float) -> str:
        payload = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
        }
        session = await self._get_session()
        try:
            async with session.post(f"{self.api_base}{self.api_path}", json=payload) as resp:
                resp.raise_for_status()
                data = await resp.json()
        except ClientResponseError as e:
            # Convert to a simple exception with a string message
            raise ValueError(f"Stable Diffusion API returned {e.status}: {e.message}")
        return data["image_url"]
    
    async def generate(self) -> str:
        prompt = self.input_value.strip()
        if not prompt:
            raise ValueError("Prompt cannot be empty.")
        # Call the cached method
        image_url = await self._call_api(
            prompt, self.width, self.height,
            self.num_inference_steps, self.guidance_scale
        )
        return f"{self.api_base}{image_url}"


    # async def generate(self)-> str:
    #     try:
    #         print("Inside Generate method.....")
    #         # pdb.set_trace()
    #         endpoint_url = "https://82e9-131-227-23-35.ngrok-free.app"
    #         api_url="/generate_url"
    #         prompt = self.input_value
    #         model_kwargs = {
    #             "width": self.width,
    #             "height": self.height,
    #             "num_inference_steps": self.num_inference_steps,
    #             "guidance_scale": self.guidance_scale,
    #         }
    #         payload = {"prompt": prompt, **model_kwargs}
    #         async with aiohttp.ClientSession() as session:
    #             async with session.post(f"{endpoint_url}{api_url}", json=payload) as resp:
    #                 if resp.status != 200:
    #                     text = await resp.text()
    #                     print(f"[DEBUG] call_api_async -> error text={text}")
    #                     raise ValueError(f"API error {resp.status}: {text}")
    #                 result = await resp.json()
    #                 if "image_url" in result:
    #                     image_url = f"{endpoint_url}{result['image_url']}"
    #                     return f"{image_url}"
                                
    #                 raise ValueError(f"Image not retrieved")
    #     except Exception as e:
    #         print(f"[ERROR] generate -> exception occurred: {str(e)}")
    #         raise
# import asyncio
# from typing import Any
# from pydantic.v1 import Field, create_model
# from langchain.agents import Tool
# from langchain_core.tools import StructuredTool
# from langflow.base.langchain_utilities.model import LCToolComponent
# from langflow.inputs.inputs import MessageTextInput, IntInput, FloatInput
# from langflow.io import Output
# from langflow.schema.message import Message
# import aiohttp

# class StableDiffusionComponent(LCToolComponent):
#     display_name = "Stable Diffusion (Text→Image)"
#     description = "Generate images from prompts via a configurable API endpoint"
#     name = "stable_diffusion"
#     icon = "Image"
#     return_direct = True  # Ensure tool output goes straight to chat

#     inputs = [
#         MessageTextInput(
#             name="prompt",
#             display_name="Prompt",
#             required=True,
#             tool_mode=True,
#         ),
#         IntInput(
#             name="width",
#             display_name="Width",
#             value=512,
#             tool_mode=True,
#         ),
#         IntInput(
#             name="height",
#             display_name="Height",
#             value=512,
#             tool_mode=True,
#         ),
#         IntInput(
#             name="num_inference_steps",
#             display_name="Steps",
#             value=50,
#             tool_mode=True,
#         ),
#         FloatInput(
#             name="guidance_scale",
#             display_name="Guidance",
#             value=7.5,
#             tool_mode=True,
#         ),
#     ]

#     outputs = [
#         Output(
#             display_name="Image URL",
#             name="image_url",
#             method="build_tool",
#         ),
#     ]

#     @staticmethod
#     async def _generate(
#         prompt: str,
#         width: int = 512,
#         height: int = 512,
#         num_inference_steps: int = 50,
#         guidance_scale: float = 7.5,
#         endpoint_url: str = "",
#     ) -> str:
#         try:
#             print("Inside Generate method...")
#             base_url = endpoint_url or "https://82e9-131-227-23-35.ngrok-free.app"
#             api_url = "/generate_url"
#             payload = {
#                 "prompt": prompt,
#                 "width": width,
#                 "height": height,
#                 "num_inference_steps": num_inference_steps,
#                 "guidance_scale": guidance_scale,
#             }
#             async with aiohttp.ClientSession() as session:
#                 async with session.post(f"{base_url}{api_url}", json=payload) as resp:
#                     if resp.status != 200:
#                         text = await resp.text()
#                         print(f"[DEBUG] API error response: {text}")
#                         raise ValueError(f"API error {resp.status}: {text}")
#                     result = await resp.json()
#                     if "image_url" in result:
#                         return f"{base_url}{result['image_url']}"
#                     raise ValueError("Image not retrieved")
#         except Exception as e:
#             print(f"[ERROR] generate -> exception occurred: {str(e)}")
#             raise

#     def build_tool(self) -> Tool:
#         def sync_generate(**kwargs: Any) -> str:
#             return asyncio.get_event_loop().run_until_complete(
#                 self._generate(**kwargs)
#             )

#         # Create args schema
#         schema = create_model(
#             "StableDiffusionSchema",
#             prompt=(str, Field(..., description="Text prompt to generate image")),
#             width=(int, Field(512, description="Image width")),
#             height=(int, Field(512, description="Image height")),
#             num_inference_steps=(int, Field(50, description="Inference steps")),
#             guidance_scale=(float, Field(7.5, description="Guidance scale")),
#             endpoint_url=(str, Field("", description="API endpoint URL")),
#         )

#         return StructuredTool.from_function(
#             func=sync_generate,
#             args_schema=schema,
#             name=self.name,
#             description=self.description,
#             return_direct=True,
#         )
