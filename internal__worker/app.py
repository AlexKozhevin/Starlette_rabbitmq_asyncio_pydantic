import asyncio
from starlette.applications import Starlette
from consumer.subscriptions import consumer_subscriptions
from rpc.subscriptions import rpc_subscriptions


class AmqpHttpServer(Starlette):
    def __init__(self, *args, **kwargs):
        loop = asyncio.get_event_loop()
        loop.create_task(consumer_subscriptions())
        loop.create_task(rpc_subscriptions())
        super().__init__(*args, **kwargs)


app = AmqpHttpServer(debug=True)

#  uvicorn app:app --reload --port 5250
