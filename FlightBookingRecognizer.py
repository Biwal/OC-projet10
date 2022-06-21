from botbuilder.ai.luis import LuisApplication, LuisRecognizer, LuisPredictionOptions
from botbuilder.core import (
    Recognizer,
    RecognizerResult,
    TurnContext,
    BotTelemetryClient,
    NullTelemetryClient,
)

from config import DefaultConfig


class FlightBookingRecognizer(Recognizer):
    def __init__(self, telemetry_client: BotTelemetryClient) -> None:
        super().__init__()
        configuration = DefaultConfig()
        luis_app = LuisApplication(
            configuration.LUIS_ID, configuration.LUIS_KEY, configuration.BOT_URL
        )
        luis_options = LuisPredictionOptions(
            include_all_intents=True,
            include_instance_data=True,
            telemetry_client=telemetry_client,
        )
        self._recognizer = LuisRecognizer(luis_app, luis_options, True)

    async def recognize(self, turn_context: TurnContext) -> RecognizerResult:
        return await self._recognizer.recognize(turn_context)
