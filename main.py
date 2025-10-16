import dotenv

dotenv.load_dotenv()

import openai

from tool_creator import ToolCreator
from schema_planner import SchemaPlanner


if __name__ == "__main__":

    task = """
    
    I need an agent to get bitcoin data for the last week and make a plot
    
    Extract required data from this curl
    
    ```
    curl --request GET 
	--url https://coingecko.p.rapidapi.com/exchanges/%7Bid%7D 
	--header 'x-rapidapi-host: coingecko.p.rapidapi.com' 
	--header 'x-rapidapi-key: 815bc6ae95msh8cb212bd58242d8p1f7c37jsn404cd3c262b0'
	```
    
    """

    client = openai.OpenAI()

    schema_planner = SchemaPlanner(client=client, model="gpt-4o-mini")
    tool_creator = ToolCreator(client=client, model="gpt-4o-mini")


    agent_plan = schema_planner.plan(task)

    print("*************** PLANNED AGENT **************")
    print(agent_plan)
    print("********************************************")

    planned_tools = agent_plan.tools


    for tool_schema in planned_tools:

        tool_code = tool_creator.generate_tool_code(tool_schema=tool_schema, task=task)

        def prepare_filename(text: str) -> str:
            def split_upper_camel_case(text: str) -> str:
                import re
                return re.sub(r'(?<!^)(?=[A-Z])', ' ', text)
            text = split_upper_camel_case(text)
            text = text.replace(" ", "_")
            text = text.replace("__", "_")
            text = text.lower()
            return text

        file_name = prepare_filename(tool_schema.name)
        tool_creator.save_code_to_file(tool_code, file_path=f"./generated_{file_name}.py")
