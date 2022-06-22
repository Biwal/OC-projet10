from botbuilder.core import (
    ActivityHandler,
    TurnContext,
    UserState,
    ConversationState,
    BotTelemetryClient,
    NullTelemetryClient,
)
from botbuilder.dialogs import DialogExtensions, ComponentDialog
from FlightBookingRecognizer import FlightBookingRecognizer
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler


class MyBot(ActivityHandler):
    def __init__(
        self,
        conversation: ConversationState,
        user_state: UserState,
        telemetry_client: BotTelemetryClient,
        dialog: ComponentDialog,
    ) -> None:

        super().__init__()
        self.LuisReg = FlightBookingRecognizer(telemetry_client)
        self.con_state = conversation
        self.user_state = user_state
        self.dialog = dialog
        self.state_prop = self.con_state.create_property("dialog_set")
        self.telemetry_client = telemetry_client
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(
            AzureLogHandler(
                connection_string="InstrumentationKey=3e7e3d0d-f7bb-497b-b60c-f5695a907970;IngestionEndpoint=https://westeurope-5.in.applicationinsights.azure.com/;LiveEndpoint=https://westeurope.livediagnostics.monitor.azure.com/"
            )
        )

    async def on_turn(self, turn_context: TurnContext):
        dialog_context = await self.dialog._dialogs.create_context(turn_context)
        if dialog_context.active_dialog is not None:
            await dialog_context.continue_dialog()
        else:
            await dialog_context.begin_dialog("main_dialog")

        await self.con_state.save_changes(turn_context)
        await self.user_state.save_changes(turn_context)

    async def on_message_activity(self, turn_context: TurnContext):
        await DialogExtensions.run_dialog(
            self.dialog,
            turn_context,
            self.con_state.create_property("DialogState"),
        )

        # Save any state changes that might have occured during the turn.
        await self.con_state.save_changes(turn_context, False)
        await self.user_state.save_changes(turn_context, False)

    @property
    def telemetry_client(self) -> BotTelemetryClient:
        """
        Gets the telemetry client for logging events.
        """
        return self._telemetry_client

    # pylint:disable=attribute-defined-outside-init
    @telemetry_client.setter
    def telemetry_client(self, value: BotTelemetryClient) -> None:
        """
        Sets the telemetry client for logging events.
        """
        if value is None:
            self._telemetry_client = NullTelemetryClient()
        else:
            self._telemetry_client = value
