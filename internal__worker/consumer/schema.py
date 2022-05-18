import json
import datetime
from simple_print import sprint
from pydantic import ValidationError
from pydantic import BaseModel
from pydantic import Field
from termcolor import cprint


class Message(BaseModel):
    username: str = Field()
    message: str = Field()
    source: str = Field()


def validate_request_schema(request_schema):
    def wrap(func):
        async def wrapped(message):
            now = datetime.datetime.now().time()
            
            sprint(f"~ {func.__name__} :: basic_ack [OK] :: {now}", c="green", s=1, p=1)
            await message.channel.basic_ack(message.delivery.delivery_tag)  # для некритичных

            json_data = None
            error = None

            try:
                json_data = json.loads(message.body) 
                validated_data = request_schema.validate(json_data).dict()
            except ValidationError as error_message:
                error = f"~ ERROR REQUEST, VALIDATION ERROR: body={message.body} error={error_message}"
            except Exception as error_message:
                error = f"~ ERROR REQUEST: body={message.body} error={error_message}"

            if not error:
                sprint(f"~ {func.__name__} :: Request {json_data}", c="yellow", s=1, p=1)
                try:
                    await func(validated_data)
                except Exception as error_message:
                    error = f"~ ERROR RESPONSE: body={message.body} error={error_message}"

            if error:
                sprint(error, c="red")
            else:
                sprint(f"~ {func.__name__} :: complete [OK]", c="green", s=1, p=1)
                
            # TODO elapsed time
            # await message.channel.basic_ack(message.delivery.delivery_tag) для критичных задач 
        return wrapped

    return wrap
