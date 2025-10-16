import importlib.util
import sys
import inspect

from openai import OpenAI

from models import ToolSchema, BaseTool

TOOL_CREATOR_SYSTEM_PROMPT = """
You are the tool creator - a module of AI agentic framework for tool creation. Here is the base class located at 
the path `models`:

```python
from pydantic import BaseModel

class ToolParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool

class BaseTool(BaseModel):
    
    identifier: str
    name: str
    description: str
    parameters: list[ToolParameter]
    
    def __call__(self, *args, **kwargs):
        raise NotImplementedError()
    
    def tool_info(self) -> str:
        return self.model_dump_json()
```

FOLLOW INSTRUCTIONS STRICTLY:
- Code style should follow PEP8 conventions
- Init parent properties via calling super constructor
- Generated class should implement required methods and set required properties in the `init` method. Fill `id`, `name`, `description`, these parameters should be imagined by you
- Don't rewrite the BaseTool class implementation, just add its path in the import
- Don't imagine non-existent classes or libraries
- Don't pass any parameters to `__init__`, only `def __init__(self)`
- Include proper type hints for all methods and parameters
- Add comprehensive docstrings for the class and methods
- Implement proper error handling for invalid inputs
- Follow the existing parameter schema format in the parameters dictionary
- Generate ONLY code in code-quotas

TESTING:

- add testcase for tool in `if __name__ == "__main__"` statement

"""

TOOL_CREATOR_USER_PROMPT = """

Generate tool using following tool schema

TOOL SCHEMA:

{tool_schema}

INITIAL USER TASK:

{task}

"""

TOOL_REFINEMENT_SYSTEM_PROMPT = """

You are a code refinement module in an AI agent framework. Review the Python code below and ensure that it behaves 
as described. Verify that the implementation fully meets the specified requirements.

FOLLOW INSTRUCTIONS STRICTLY:
- Ensure all required imports are added
- Generate ONLY code in code-quotas

"""

TOOL_REFINEMENT_USER_PROMPT = """

TOOL SCHEMA:

{tool_schema}

TOOL CODE:

```python
{code}
```

"""

class ToolCreator:
    def __init__(self, client: OpenAI, model: str):
        self.client = client
        self.model = model

    def generate_tool_code(self, tool_schema: ToolSchema, task: str) -> str:
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": TOOL_CREATOR_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": TOOL_CREATOR_USER_PROMPT.format(tool_schema=tool_schema.model_dump_json(), task=task),
                },
            ]
        )

        code = response.output_text.split("```python")[1].split("```")[0]

        refined_code = self._run_refinement_loop(tool_schema, code)

        return refined_code


    def _run_refinement_loop(self,
                             tool_schema: ToolSchema,
                             code: str,
                             refinement_count: int = 1) -> str:

        code_for_refinement = code

        for _ in range(refinement_count):
            response = self.client.responses.parse(
                model=self.model,
                input=[
                    {
                        "role": "system",
                        "content": TOOL_REFINEMENT_SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": TOOL_REFINEMENT_USER_PROMPT.format(tool_schema=tool_schema.model_dump_json(),
                                                                      code=code_for_refinement),
                    }
                ]
            )

            code_for_refinement = response.output_text.split("```python")[1].split("```")[0]

        return code_for_refinement

    @staticmethod
    def save_code_to_file(code: str, python_tool_file_path: str):
        if not str(python_tool_file_path).endswith(".py"):
            raise ValueError("file_path must end with .py")
        with open(python_tool_file_path, "w", encoding="utf-8") as file:
            file.write(code)

    @staticmethod
    def get_tool_instance(python_tool_file_path: str) -> BaseTool:

        module_name = "dynamic_module"
        spec = importlib.util.spec_from_file_location(module_name, python_tool_file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        classes = [
            name for name, obj in inspect.getmembers(module, inspect.isclass)
            if obj.__module__ == module_name
        ]

        ToolClass = getattr(module, classes[0])

        return ToolClass()

