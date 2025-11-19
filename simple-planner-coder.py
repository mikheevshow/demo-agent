import json
import logging
from datetime import datetime
import platform
import os

import dotenv

from llm.call import LLMClient
from tool_v3.open_ai_tool_decorator import openai_tool
from tools.ask_user_tool import ask_user_tool
from tools.terminal_tools import terminal_tool
from utils.logger import get_logger

dotenv.load_dotenv()

logger = logging.getLogger(__name__)


def get_system_context():
    system_info = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "architecture": platform.architecture()[0],
        "processor": platform.processor(),
        "machine": platform.machine(),
        "python_version": platform.python_version()
    }

    env_info = {
        "current_directory": os.getcwd(),
        "username": os.getenv('USERNAME') or os.getenv('USER'),
        "home_directory": os.path.expanduser('~'),
        "temp_directory": os.getenv('TEMP') or os.getenv('TMP')
    }

    current_time = datetime.now()
    time_info = {
        "current_datetime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "current_date": current_time.strftime("%Y-%m-%d"),
        "current_time": current_time.strftime("%H:%M:%S"),
        "timezone": str(current_time.astimezone().tzinfo),
        "weekday": current_time.strftime("%A"),
        "is_weekend": current_time.weekday() >= 5
    }

    context = {
        "platform_info": system_info,
        "environment_info": env_info,
        "time_info": time_info,
        "timestamp": current_time.isoformat()
    }

    return context


system_context = get_system_context()

SYSTEM_INFO_PROMPT = """
    You are helpfully assistant\n
    
    TOOLS INFORMATION:
    
    - `ask_user_tool` - ask user if additional information required. Ask the user just one time.
    - `finish_task_tool` - call this tool if you are ready to finish the task. Pass the final response as tool parameter.
    
    DEPENDENCIES:
    
    SYSTEM INFORMATION:

    PLATFORM INFO:
    - Operating System: {system} {release}
    - OS Version: {version}
    - Architecture: {architecture}
    - Processor: {processor}
    - Python Version: {python_version}
    
    ENVIRONMENT INFO:
    - Current Directory: {current_directory}
    - User: {username}
    - Home Directory: {home_directory}
    
    TIME INFORMATION:
    - Current Date and Time: {current_datetime}
    - Timezone: {timezone}
    - Weekday: {weekday}
    - Is Weekend: {is_weekend}
    
    Use this information for:
    1. Providing contextually relevant responses
    2. Considering temporal aspects (season, time of day)
    3. Adapting to the user's operating system
    4. Taking into account file structure when working with paths
    
""".format(
    system=system_context['platform_info']['system'],
    release=system_context['platform_info']['release'],
    version=system_context['platform_info']['version'],
    architecture=system_context['platform_info']['architecture'],
    processor=system_context['platform_info']['processor'],
    python_version=system_context['platform_info']['python_version'],
    current_directory=system_context['environment_info']['current_directory'],
    username=system_context['environment_info']['username'],
    home_directory=system_context['environment_info']['home_directory'],
    current_datetime=system_context['time_info']['current_datetime'],
    timezone=system_context['time_info']['timezone'],
    weekday=system_context['time_info']['weekday'],
    is_weekend=system_context['time_info']['is_weekend']
)

CODER_SYSTEM_PROMPT = """
    You are helpfully assistant\n
    
    SYSTEM INFORMATION:

    PLATFORM INFO:
    - Operating System: {system} {release}
    - OS Version: {version}
    - Architecture: {architecture}
    - Processor: {processor}
    - Python Version: {python_version}
    
    ENVIRONMENT INFO:
    - Current Directory: {current_directory}
    - User: {username}
    - Home Directory: {home_directory}
    
    TIME INFORMATION:
    - Current Date and Time: {current_datetime}
    - Timezone: {timezone}
    - Weekday: {weekday}
    - Is Weekend: {is_weekend}
    
    DEPENDENCIES:
    
    You work in `uv` environment. If some dependencies need to be checked or install just use `uv add <requirement>` 
    or `uv add -r requirements.txt`. Do not create separate environments.
    
    Use this information for:
    1. Providing contextually relevant responses
    2. Considering temporal aspects (season, time of day)
    3. Adapting to the user's operating system
    4. Taking into account file structure when working with paths
    
    """.format(
    system=system_context['platform_info']['system'],
    release=system_context['platform_info']['release'],
    version=system_context['platform_info']['version'],
    architecture=system_context['platform_info']['architecture'],
    processor=system_context['platform_info']['processor'],
    python_version=system_context['platform_info']['python_version'],
    current_directory=system_context['environment_info']['current_directory'],
    username=system_context['environment_info']['username'],
    home_directory=system_context['environment_info']['home_directory'],
    current_datetime=system_context['time_info']['current_datetime'],
    timezone=system_context['time_info']['timezone'],
    weekday=system_context['time_info']['weekday'],
    is_weekend=system_context['time_info']['is_weekend']
)

system = {
    "role": "system",
    "content": """
    You are helpfully assistant\n
    
    SYSTEM INFORMATION:

    PLATFORM INFO:
    - Operating System: {system} {release}
    - OS Version: {version}
    - Architecture: {architecture}
    - Processor: {processor}
    - Python Version: {python_version}
    
    ENVIRONMENT INFO:
    - Current Directory: {current_directory}
    - User: {username}
    - Home Directory: {home_directory}
    
    TIME INFORMATION:
    - Current Date and Time: {current_datetime}
    - Timezone: {timezone}
    - Weekday: {weekday}
    - Is Weekend: {is_weekend}
    
    DEPENDENCIES:
    
    You work in `uv` environment. If some dependencies need to be checked or install just use `uv add <requirement>` 
    or `uv add -r requirements.txt`. Do not create separate environments.
    
    Use this information for:
    1. Providing contextually relevant responses
    2. Considering temporal aspects (season, time of day)
    3. Adapting to the user's operating system
    4. Taking into account file structure when working with paths
    
    """.format(
        system=system_context['platform_info']['system'],
        release=system_context['platform_info']['release'],
        version=system_context['platform_info']['version'],
        architecture=system_context['platform_info']['architecture'],
        processor=system_context['platform_info']['processor'],
        python_version=system_context['platform_info']['python_version'],
        current_directory=system_context['environment_info']['current_directory'],
        username=system_context['environment_info']['username'],
        home_directory=system_context['environment_info']['home_directory'],
        current_datetime=system_context['time_info']['current_datetime'],
        timezone=system_context['time_info']['timezone'],
        weekday=system_context['time_info']['weekday'],
        is_weekend=system_context['time_info']['is_weekend']
    )
}

requirements_clarification_prompt = "Если у тебя есть уточняющие вопросы, задай их через инструмент `ask_user_tool`"


class Planner:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.logger = get_logger("baseline-planner")

    @openai_tool
    def finish_task_tool(self, answer: str) -> str:
        """
            Call this tool if you ready to finish your task
            Args:
            final_answer (str): Pass your conversation answer here
        """
        return answer

    def plan(self, task: str, clarify_requirements: bool = True, ask_user_times: int = 1, max_iter: int = 100) -> tuple[
        str, list[dict[str, str]]]:

        messages = [
            {
                "role": "system",
                "content": SYSTEM_INFO_PROMPT
            },
            {
                "role": "user",
                "content": """

                Мне нужно: {task}
            
                Как бы ты решал эту задачу?
            
                {clarify_requirements}
    
                """.format(
                    task=task,
                    clarify_requirements=requirements_clarification_prompt if clarify_requirements else "",
                )
            }
        ]

        _tools = [self.finish_task_tool]

        if clarify_requirements:
            _tools.append(ask_user_tool)

        user_asked_times: int = 0

        for step in range(max_iter):

            self.logger.info(f"Planner step {step} / {max_iter}")

            response = llm_client.run_llm_with_tools(
                messages=messages,
                tools=_tools,
                tool_choice="required",
            )

            msg = response.choices[0].message

            assistant_message = {"role": "assistant"}

            if msg.content:
                assistant_message["content"] = msg.content

            if msg.tool_calls:
                assistant_message["tool_calls"] = [tc.model_dump() for tc in msg.tool_calls]

            messages.append(assistant_message)

            if msg.tool_calls:
                for tc in msg.tool_calls:

                    tool = {tool.__name__: tool for tool in _tools}[
                        tc.function.name
                    ]
                    args = json.loads(tc.function.arguments)

                    if not tool:
                        result = f"Unknown tool: {tool.__name__}"
                        self.logger.error(f"Unknown tool requested: {tool.__name__}")
                    else:
                        try:
                            self.logger.info(
                                "Running tool: %s with args: %s", tool.__name__, args
                            )
                            if tool.__name__ == "ask_user_tool":
                                if user_asked_times > 0:
                                    result = f"Exceeded attempts to clarify info from user"
                                else:
                                    result = tool(**args)
                                    user_asked_times += 1
                            else:
                                result = tool(**args)
                            self.logger.info(
                                "Tool %s completed. Tool result %s",
                                tool.__name__,
                                result,
                            )
                        except Exception as e:
                            result = f"Tool execution failed: {e}"
                            self.logger.exception("Tool %s failed:", tool.__name__)

                    if tool.__name__ == "finish_task_tool":
                        self.logger.info("Planner give the final answer: %s", result)
                        return result, messages.copy()

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": str(result),
                        }
                    )

                continue

        raise RuntimeError("Planner can't finish the task")

class Coder:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.logger = get_logger("coder")

    @openai_tool
    def finish_task_tool(self, answer: str) -> str:
        """
            Call this tool if you ready to finish your task
            Args:
                answer (str): Pass your conversation answer here
        """
        return answer

    def code(self, user_task: str, plan: str, max_iters: int = 100):
        messages = [
            {
                "role": "system",
                "content": CODER_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": """
                
                Как решить такую задачу?
                
                {user_task}
                
                """.format(user_task=user_task),
            },
            {
                "role": "assistant",
                "content": plan
            },
            {
                "role": "user",
                "content": """
                Напиши код решения. 
                - Если в задаче требуется создать AI агента, то используй LangGraph. 
                - Ecли решение будет использовать LLM, то используй 
                - Добавь dotenv и загрузку переменных окружения gpt-5-mini
                - В условии `if __name__ == '__main__' пропиши код запуска`
                """
            }
        ]

        for i in range(max_iters):

            self.logger.info(f"Coder step {i} / {max_iters}")

            if i in {0, 1}:
                tools = []
                response = llm_client.client.chat.completions.create(
                    messages=messages,
                    model=llm_client.model,
                )
            else:
                tools = [
                    ask_user_tool,
                    terminal_tool,
                    self.finish_task_tool,
                ]
                response = llm_client.run_llm_with_tools(
                    messages=messages,
                    tools=tools,
                    tool_choice="required",
                )

            msg = response.choices[0].message

            assistant_message = {"role": "assistant"}

            if msg.content:
                assistant_message["content"] = msg.content

            if msg.tool_calls:
                assistant_message["tool_calls"] = [
                    tc.model_dump() for tc in msg.tool_calls
                ]

            messages.append(assistant_message)

            if msg.tool_calls:
                for tc in msg.tool_calls:
                    tool = {tool.__name__: tool for tool in tools}[
                        tc.function.name
                    ]
                    args = json.loads(tc.function.arguments)

                    if not tool:
                        result = f"Unknown tool: {tool.__name__}"
                        logger.error(f"Unknown tool requested: {tool.__name__}")
                    else:
                        try:
                            logger.info(
                                "Running tool: %s with args: %s", tool.__name__, args
                            )
                            result = tool(**args)
                            logger.info(
                                "Tool %s completed. Tool result %s",
                                tool.__name__,
                                result,
                            )
                        except Exception as e:
                            result = f"Tool execution failed: {e}"
                            logger.exception("Tool %s failed:", tool.__name__)

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": str(result),
                        }
                    )

                    if tool.__name__ == "finish_task_tool":
                        logger.info(f"Finishing tool {tool.__name__}")
                        return result, messages
                continue

            if i in {0}:
                messages.append(
                    {
                        "role": "user",
                        "content": "Какие действия еще нужно сделать, чтобы код заработал?"
                    }
                )

            if i in {1}:
                messages.append(
                    {
                        "role": "user",
                        "content": """
                        Выполнить все необходимые действия, чтобы сделать код рабочим.
                        Для этого я хочу получить необходимые артефакты в папке '{cwd}/agent_artifacts_{date_stamp}'. Предварительно проверь наличие этой
                        директории.
                    
                        Доступные инструменты:
                        - `ask_user` - спросить детали у пользователя
                        - `terminal_tool` - выполнение команд в терминале
                        - `finish_task_tool` - вызови этот инструмент, когда захочешь окончательно завершить запрос пользователя
                    
                        При выполнении различных команд через `terminal_tool` не группируй много команд в одну
                    
                        Завершение:
                        Вызови `finish_task_tool` когда все пункты для реализации задачи пользователя выполнены.
                        """.format(cwd=os.getcwd(), date_stamp=datetime.now().strftime("%d%m%Y_%H%M"))
                    }
                )

        raise RuntimeError("Could not find a suitable tool")


if __name__ == "__main__":

    task = input("Что делаем?\n>>> ")

    LLM_CONFIG = {
        "base_url": os.getenv("PROXY_BASE_URL"),
        "api_key": os.getenv("PROXY_API_KEY"),
        "model": "gpt-5",
    }

    llm_client = LLMClient(
        model=LLM_CONFIG["model"],
        base_url=LLM_CONFIG["base_url"],
        api_key=LLM_CONFIG["api_key"],
    )

    planner = Planner(llm_client)
    planned_task, _ = planner.plan(task)

    print(planned_task)

    coder = Coder(llm_client)
    coder_result, _ = coder.code(user_task=task, plan=planned_task)

    print(coder_result)
