import dotenv

dotenv.load_dotenv()

import openai

from tool_creator import ToolCreator
from schema_planner import SchemaPlanner


if __name__ == "__main__":

    task = """
    Create an agent which will get user input and send it as a message to Telegram Bot.
    
    Here are required credentials:
    
    Telegram Bot Token: 7623310610:AAGkVMUFBLxnAVNsUfnh8Rp_JQ3WFo9uDC0
    Telegram Chat id: -4910128354
    
    OPEN API SPEC:
    
    ```yaml
    openapi: 3.0.3
info:
  title: Telegram Bot API
  description: |
    Официальный Telegram Bot API.  
    Документация: https://core.telegram.org/bots/api  
    Этот файл описывает метод `sendMessage`.
  version: 6.9  # актуальная версия Bot API на 2025 год
  contact:
    name: Telegram Bot API Team
    url: https://core.telegram.org/bots

servers:
  - url: https://api.telegram.org
    description: Официальный сервер Telegram Bot API

paths:
  /bot{token}/sendMessage:
    post:
      summary: Отправить текстовое сообщение
      description: |
        Используйте этот метод для отправки текстовых сообщений.  
        Токен бота должен быть получен от [@BotFather](https://t.me/BotFather).
      operationId: sendMessage
      parameters:
        - name: token
          in: path
          required: true
          schema:
            type: string
            pattern: '^[0-9]+:[A-Za-z0-9_-]{35,35}$'  # примерная валидация токена
          description: Токен вашего Telegram-бота (например: `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`)
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SendMessageRequest'
          application/x-www-form-urlencoded:
            schema:
              $ref: '#/components/schemas/SendMessageRequest'
      responses:
        '200':
          description: Успешный ответ от Telegram
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TelegramSuccessResponse'
        '400':
          description: Неверный запрос (например, отсутствует chat_id или text)
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TelegramErrorResponse'
        '401':
          description: Недействительный токен
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TelegramErrorResponse'
        '403':
          description: Бот не может отправить сообщение в этот чат (например, пользователь заблокировал бота)
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TelegramErrorResponse'
        '429':
          description: Слишком много запросов (превышен лимит)
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TelegramErrorResponse'
        default:
          description: Ошибка Telegram Bot API
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TelegramErrorResponse'

components:
  schemas:
    SendMessageRequest:
      type: object
      required:
        - chat_id
        - text
      properties:
        chat_id:
          oneOf:
            - type: integer
              description: Числовой ID чата (например, 123456789)
            - type: string
              description: Username канала в формате @channelusername или ID в виде строки
          example: 123456789
        text:
          type: string
          maxLength: 4096
          description: Текст сообщения
          example: "Привет! Это сообщение через официальный Telegram Bot API."
        parse_mode:
          type: string
          enum: [MarkdownV2, HTML, Markdown]
          description: |
            Режим разбора сущностей в тексте.  
            **Важно**: `Markdown` устарел; рекомендуется `MarkdownV2` или `HTML`.
          example: "HTML"
        entities:
          type: array
          items:
            $ref: '#/components/schemas/MessageEntity'
          description: Список специальных сущностей (например, упоминаний, ссылок)
        disable_web_page_preview:
          type: boolean
          description: Отключает предпросмотр ссылок
        disable_notification:
          type: boolean
          description: Отправить без звука уведомления
        protect_content:
          type: boolean
          description: Защитить сообщение от пересылки и сохранения
        reply_parameters:
          $ref: '#/components/schemas/ReplyParameters'
        reply_markup:
          $ref: '#/components/schemas/InlineKeyboardMarkup'

    MessageEntity:
      type: object
      required:
        - type
        - offset
        - length
      properties:
        type:
          type: string
          description: Тип сущности (например, "bold", "url", "mention")
        offset:
          type: integer
          description: Смещение в символах от начала текста
        length:
          type: integer
          description: Длина сущности в символах
        url:
          type: string
          description: URL для типа "text_link"
        user:
          $ref: '#/components/schemas/User'

    ReplyParameters:
      type: object
      properties:
        message_id:
          type: integer
          description: ID сообщения, на которое нужно ответить
        chat_id:
          oneOf:
            - type: integer
            - type: string
          description: ID чата (если ответ в другой чат)

    InlineKeyboardMarkup:
      type: object
      properties:
        inline_keyboard:
          type: array
          items:
            type: array
            items:
              $ref: '#/components/schemas/InlineKeyboardButton'

    InlineKeyboardButton:
      type: object
      properties:
        text:
          type: string
        url:
          type: string
        callback_
          type: string
        # ... другие поля (см. официальную документацию)

    User:
      type: object
      properties:
        id:
          type: integer
        is_bot:
          type: boolean
        first_name:
          type: string
        last_name:
          type: string
        username:
          type: string

    TelegramSuccessResponse:
      type: object
      properties:
        ok:
          type: boolean
          example: true
        result:
          $ref: '#/components/schemas/Message'

    TelegramErrorResponse:
      type: object
      properties:
        ok:
          type: boolean
          example: false
        error_code:
          type: integer
          example: 400
        description:
          type: string
          example: "Bad Request: chat not found"

    Message:
      type: object
      properties:
        message_id:
          type: integer
        message_thread_id:
          type: integer
        from:
          $ref: '#/components/schemas/User'
        sender_chat:
          $ref: '#/components/schemas/Chat'
        date:
          type: integer
          description: Unix timestamp
        chat:
          $ref: '#/components/schemas/Chat'
        text:
          type: string
        # ... другие поля (entities, reply_markup и т.д.)

    Chat:
      type: object
      properties:
        id:
          type: integer
        type:
          type: string
          enum: [private, group, supergroup, channel]
        title:
          type: string
        username:
          type: string
        first_name:
          type: string
        last_name:
          type: string
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
