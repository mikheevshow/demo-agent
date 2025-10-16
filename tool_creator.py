from openai import OpenAI

from models import ToolSchema


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

        print(response)

        return response.output_text.split("```python")[1].split("```")[0]

    @staticmethod
    def save_code_to_file(code: str, file_path: str):
        if not str(file_path).endswith(".py"):
            raise ValueError("file_path must end with .py")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(code)

