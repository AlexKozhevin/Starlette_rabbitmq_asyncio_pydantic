from consumer import schema
from consumer import methods


@schema.validate_request_schema(schema.Message)
async def pow_chat_message(validated_data):
    await methods.pow_chat_message(validated_data)
