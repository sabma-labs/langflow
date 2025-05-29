import os
from dotenv import load_dotenv
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
    BoolInput
)
load_dotenv()
class StableDiffusionComponent(Component):
    display_name = "Stable Diffusion (Text→Image)"
    description = "Generate images from prompts via Hugging Face Inference API or local fallback."
    icon = "Image"
    name = "StableDiffusion"
    return_direct = True
    api_base = os.getenv("STABLE_DIFFUSION_ENDPOINT")
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

