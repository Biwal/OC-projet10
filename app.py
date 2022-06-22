import sys
import traceback
from datetime import datetime

from aiohttp import web
from aiohttp.web import Request, Response, json_response
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    UserState,
    TurnContext,
    BotFrameworkAdapter,
    ConversationState,
    MemoryStorage,
    TelemetryLoggerMiddleware,
)
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.schema import Activity, ActivityTypes
from botbuilder.applicationinsights import ApplicationInsightsTelemetryClient
from botbuilder.integration.applicationinsights.aiohttp import (
    AiohttpTelemetryProcessor,
    bot_telemetry_middleware,
)
from bot import MyBot
from config import DefaultConfig
import logging
from BookingDialog import BookingDialog
from opencensus.ext.azure.log_exporter import AzureLogHandler


CONFIG = DefaultConfig()
SETTINGS = BotFrameworkAdapterSettings("", "")
# SETTINGS = BotFrameworkAdapterSettings(CONFIG.APP_ID, CONFIG.APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)

logger = logging.getLogger(__name__)

logger.addHandler(AzureLogHandler(
    connection_string= "InstrumentationKey=3e7e3d0d-f7bb-497b-b60c-f5695a907970;IngestionEndpoint=https://westeurope-5.in.applicationinsights.azure.com/;LiveEndpoint=https://westeurope.livediagnostics.monitor.azure.com/")
)


async def on_error(context: TurnContext, error: Exception):
    # This check writes out errors to console log .vs. app insights.
    # NOTE: In production environment, you should consider logging this to Azure
    #       application insights.
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()

    # Send a message to the user
    await context.send_activity("The bot encountered an error or bug.")
    await context.send_activity(
        "To continue to run this bot, please fix the bot source code."
    )
    # Send a trace activity if we're talking to the Bot Framework Emulator
    if context.activity.channel_id == "emulator":
        # Create a trace activity that contains the error object
        trace_activity = Activity(
            label="TurnError",
            name="on_turn_error Trace",
            timestamp=datetime.utcnow(),
            type=ActivityTypes.trace,
            value=f"{error}",
            value_type="https://www.botframework.com/schemas/error",
        )
        # Send a trace activity, which will be displayed in Bot Framework Emulator
        await context.send_activity(trace_activity)


ADAPTER.on_turn_error = on_error

MEMORY = MemoryStorage()
CONMEMORY = ConversationState(MEMORY)
USER_STATE = UserState(MEMORY)
TELEMETRY_CLIENT = ApplicationInsightsTelemetryClient(
    "3e7e3d0d-f7bb-497b-b60c-f5695a907970",
    telemetry_processor=AiohttpTelemetryProcessor(),
    client_queue_size=10,
)
TELEMETRY_LOGGER_MIDDLEWARE = TelemetryLoggerMiddleware(
    telemetry_client=TELEMETRY_CLIENT, log_personal_information=True
)
ADAPTER.use(TELEMETRY_LOGGER_MIDDLEWARE)

DIALOG = BookingDialog(telemetry_client=TELEMETRY_CLIENT, con_state=CONMEMORY)
TELEMETRY_CLIENT.main_dialog = DIALOG
# DIALOG.add()

BOT = MyBot(CONMEMORY, USER_STATE, TELEMETRY_CLIENT, DIALOG)
# Listen for incoming requests on /api/messages
async def messages(req: Request) -> Response:
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return Response(status=415)

    activity = Activity().deserialize(body)
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

    try:
        response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
        if response:
            return json_response(data=response.body, status=response.status)
        return Response(status=201)
    except Exception as exception:
        raise exception


async def init_func(argv):
    APP = web.Application(
        middlewares=[bot_telemetry_middleware, aiohttp_error_middleware]
    )
    APP.router.add_post("/api/messages", messages)
    return APP


if __name__ == "__main__":
    APP = init_func(None)

    try:
        logger.setLevel(logging.DEBUG)
        logger.info('Application started correctly.')
        web.run_app(APP, host="localhost", port=CONFIG.PORT)
    except Exception as error:
        raise error
