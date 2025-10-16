from openai import OpenAI
from models import AgentSchema


AGENT_PLANNER_SYSTEM_PROMPT = """

You are an AI agent planner. You are a part of AI framework for agent creation. Your aim to build an agent based on user
requirements. Describe all agent properties and available tools.

"""

AGENT_PLANNER_USER_PROMPT = """

USER TASK:

{user_task}

"""

class AgentSchemaPlanner:

    def __init__(self, client: OpenAI, model: str):
        self.client = client
        self.model = model

    def plan(self, task: str) -> AgentSchema:

        response = self.client.responses.parse(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": AGENT_PLANNER_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": AGENT_PLANNER_USER_PROMPT.format(user_task=task),
                },
            ],
            text_format=AgentSchema
        )

        return response.output_parsed