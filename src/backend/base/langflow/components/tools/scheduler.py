from langflow.custom import Component
from langflow.inputs import DropdownInput, MultilineInput, SecretStrInput, StrInput, MessageInput, CodeInput
from langflow.io import Output
from langflow.schema import Data
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from langchain_experimental.utilities import PythonREPL
import importlib

class SchedulerComponent(Component):
    display_name = "Scheduler"
    description = "Scheduler Component"
    icon = "timer"
    name = "Scheduler"
    # legacy = True

    inputs = [
        StrInput(
            name="global_imports",
            display_name="Global Imports",
            info="A comma-separated list of modules to import globally, e.g. 'math,numpy,pandas'.",
            value="math,pandas",
            required=True,
        ),
        CodeInput(
            name="python_code",
            display_name="Python Code",
            info="The Python code to execute. Only modules specified in Global Imports can be used.",
            value="print('Hello, World!')",
            tool_mode=True,
            required=True,
        ),

    ]

    outputs=[
        Output(display_name="Data", name="data", method="start_scheduling"),
    ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        self.scheduler = AsyncIOScheduler(event_loop=loop)
        self.started = False

    def get_globals(self, global_imports: str | list[str]) -> dict:
        """Create a globals dictionary with only the specified allowed imports."""
        global_dict = {}

        try:
            if isinstance(global_imports, str):
                modules = [module.strip() for module in global_imports.split(",")]
            elif isinstance(global_imports, list):
                modules = global_imports
            else:
                msg = "global_imports must be either a string or a list"
                raise TypeError(msg)

            for module in modules:
                try:
                    imported_module = importlib.import_module(module)
                    global_dict[imported_module.__name__] = imported_module
                except ImportError as e:
                    msg = f"Could not import module {module}: {e!s}"
                    raise ImportError(msg) from e

        except Exception as e:
            print(f"Error in global imports: {e!s}")
            raise
        else:
            print(f"Successfully imported modules: {list(global_dict.keys())}")
            return global_dict

    def job_function(self):
        print("Scheduled job executed!")

        try:
            globals_ = self.get_globals(self.global_imports)
            python_repl = PythonREPL(_globals=globals_)
            result = python_repl.run(self.python_code)
            result = result.strip() if result else ""

            print("Code execution completed successfully")
            return Data(data={"result": result})

        except ImportError as e:
            error_message = f"Import Error: {e!s}"
            print(error_message)
            return Data(data={"error": error_message})

        except SyntaxError as e:
            error_message = f"Syntax Error: {e!s}"
            print(error_message)
            return Data(data={"error": error_message})

        except (NameError, TypeError, ValueError) as e:
            error_message = f"Error during execution: {e!s}"
            print(error_message)
            return Data(data={"error": error_message})

    def start_scheduling(self) -> Data:
        if not self.started:
            self.scheduler.add_job(self.job_function, 'interval', seconds=3)
            self.scheduler.start()
            self.started = True
            print("Scheduler started.")

        return Data(data=None)
