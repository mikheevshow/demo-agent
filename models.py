from pydantic import BaseModel

# Agent schemas

class ToolParameterSchema(BaseModel):
    name: str
    type: str
    description: str
    required: str

class ToolSchema(BaseModel):
    name: str
    description: str
    parameters: list[ToolParameterSchema]
    implementation_details_description: str

class AgentSchema(BaseModel):
    name: str
    description: str
    system_prompt: str
    tools: list[ToolSchema]


# Base tool class

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
