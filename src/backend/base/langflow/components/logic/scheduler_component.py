import asyncio
import json
from datetime import datetime, timezone

from croniter import croniter
from loguru import logger

from langflow.custom import Component
from langflow.helpers.flow import run_flow
from langflow.io import BoolInput, DropdownInput, IntInput, MessageTextInput, Output
from langflow.schema import Data


class SchedulerComponent(Component):
    display_name = "Scheduler"
    description = "Schedule execution of a selected flow based on cron or interval."
    icon = "clock"
    name = "Scheduler"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._task = None
        self._stop_event = asyncio.Event()
        self._last_output = None

    inputs = [
        MessageTextInput(
            name="cron_expression",
            display_name="Cron Expression",
            info="Cron expression for scheduling (e.g., */5 * * * *). Leave empty if using interval.",
        ),
        IntInput(
            name="interval_seconds",
            display_name="Interval (Seconds)",
            info="Interval in seconds between flow executions. Ignored if cron is set.",
            value=60,
        ),
        DropdownInput(
            name="flow_name",
            display_name="Flow Name",
            info="The name of the flow to run.",
            options=[],
            refresh_button=True,
            real_time_refresh=True,
        ),
        BoolInput(
            name="auto_start",
            display_name="Auto Start",
            info="Automatically start the scheduler when the component loads.",
            value=False,
        ),
        MessageTextInput(
            name="input_params",
            display_name="Input Parameters (JSON)",
            info="Optional input parameters for the flow, in JSON format.",
        ),
    ]

    outputs = [Output(name="schedule_output", display_name="Scheduled Output", method="output_message")]

    async def on_start(self):
        if getattr(self, "auto_start", False):
            await self.start_scheduler()

    async def start_scheduler(self):
        if self._task and not self._task.done():
            return  # Already running
        self._stop_event.clear()
        self._task = asyncio.create_task(self._scheduler_loop())

    def stop_scheduler(self):
        if self._task and not self._task.done():
            self._stop_event.set()

    async def _scheduler_loop(self):
        try:
            cron = getattr(self, "cron_expression", None)
            interval = getattr(self, "interval_seconds", 60)
            flow_name = getattr(self, "flow_name", None)
            input_params = getattr(self, "input_params", None)

            tweaks = self.parse_input_params(input_params)

            if not flow_name:
                logger.error("No flow selected for scheduling.")
                return

            if cron:
                base_time = datetime.now(timezone.utc)
                cron_iter = croniter(cron, base_time)

                while not self._stop_event.is_set():
                    next_time = cron_iter.get_next(datetime)
                    wait_seconds = (next_time - datetime.now(timezone.utc)).total_seconds()
                    if wait_seconds > 0:
                        await asyncio.wait([self._stop_event.wait()], timeout=wait_seconds)
                    if not self._stop_event.is_set():
                        await self.trigger_flow(flow_name, tweaks)
            else:
                while not self._stop_event.is_set():
                    await self.trigger_flow(flow_name, tweaks)
                    await asyncio.wait([self._stop_event.wait()], timeout=interval)

        except Exception as e:  # noqa: BLE001 - safeguard to prevent scheduler crash
            logger.exception(f"Scheduler error: {e}")

    async def trigger_flow(self, flow_name: str, tweaks: dict | None = None):
        try:
            logger.info(f"Triggering scheduled flow: {flow_name}")
            result = await run_flow(
                inputs=None,
                output_type="all",
                flow_id=None,
                flow_name=flow_name,
                tweaks=tweaks,
                user_id=str(self.user_id),
                session_id=self.graph.session_id or self.session_id,
            )
            self.status = f"Triggered flow: {flow_name}"
            self._last_output = result
        except Exception as e:  # noqa: BLE001 - safeguard to prevent scheduler crash
            logger.exception(f"Failed to run scheduled flow: {e}")
            self.status = f"Error: {e}"
            self._last_output = None

    def parse_input_params(self, params_text: str | None) -> dict:
        if not params_text:
            return {}
        try:
            return json.loads(params_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse input parameters: {e}")
            return {}

    async def output_message(self) -> Data:
        if self._last_output:
            try:
                first_result = self._last_output[0]
                if hasattr(first_result, "outputs"):
                    outputs = [output.data for output in first_result.outputs if output]
                    return Data(data={"flow_outputs": outputs})
            except Exception as e:  # noqa: BLE001 - safeguard to prevent scheduler crash
                logger.exception(f"Failed to parse flow output: {e}")
                return Data(data={"status": self.status or "No status"})
        return Data(data={"status": self.status or "No status"})

    async def update_build_config(self, build_config: dict, _field_value: str, field_name: str | None = None) -> dict:
        if field_name == "flow_name":
            build_config["flow_name"]["options"] = await self.get_flow_names()
        return build_config

    async def get_flow_names(self) -> list[str]:
        flow_data = await self.alist_flows()
        return [flow.data["name"] for flow in flow_data]
