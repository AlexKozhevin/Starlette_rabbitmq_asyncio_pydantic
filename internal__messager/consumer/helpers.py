import asyncio
import uuid
import aiormq
import json
import aiormq.types
from settings import AMQP_URI 
from settings import UNIQUE_PREFIX


class FibonacciRpcClient:
    def __init__(self):
        self.connection = None      # type: aiormq.Connection
        self.channel = None         # type: aiormq.Channel
        self.callback_queue = ''
        self.futures = {}
        self.loop = asyncio.get_event_loop()

    async def connect(self):
        self.connection = await aiormq.connect(AMQP_URI)

        self.channel = await self.connection.channel()
        declare_ok = await self.channel.queue_declare(
                                                      exclusive=True,
                                                      auto_delete=True,
                                                      queue=f"{UNIQUE_PREFIX}:my_RPC_queue"
                                                      )

        await self.channel.basic_consume(declare_ok.queue, self.on_response)

        self.callback_queue = declare_ok.queue

        return self

    async def on_response(self, message: aiormq.types.DeliveredMessage):
        future = self.futures.pop(message.header.properties.correlation_id)
        future.set_result(message.body)

    async def call(self, outcoming_message_dict, routing_key):
        correlation_id = str(uuid.uuid4())
        future = self.loop.create_future()

        self.futures[correlation_id] = future
        outcoming_message_bytes = json.dumps(outcoming_message_dict).encode()
        await self.channel.basic_publish(
            outcoming_message_bytes, routing_key=routing_key,
            properties=aiormq.spec.Basic.Properties(
                content_type='text/plain',
                correlation_id=correlation_id,
                reply_to=self.callback_queue,
            )
        )
        body = await future
        incoming_message_dict = json.loads(body.decode())
        return incoming_message_dict
