from typing import List
from botbuilder.dialogs import (
    WaterfallDialog,
    WaterfallStepContext,
    ComponentDialog,
    DialogSet,
)
from botbuilder.dialogs.prompts import ConfirmPrompt, PromptOptions
from botbuilder.core import MessageFactory, BotTelemetryClient, NullTelemetryClient
from FlightBookingRecognizer import FlightBookingRecognizer
from Prompts import AirportsPrompt, DatesPrompt, BudgetPrompt
from utils import get_entity_value

class BookingDialog(ComponentDialog):
    """Flight booking implementation."""

    def __init__(
        self,
        dialog_id: str = None,
        telemetry_client: BotTelemetryClient = NullTelemetryClient(),
        con_state=None,
    ):
        super(ComponentDialog, self).__init__(ComponentDialog.__name__)
        self._recognizer = FlightBookingRecognizer(telemetry_client)
        self.telemetry_client = telemetry_client
        self._dialogs = DialogSet(con_state.create_property("dialog_set"))
        self.initial_dialog_id = "main_dialog"

        airports_prompt = AirportsPrompt("airports_prompt", self._recognizer, telemetry_client= self.telemetry_client)
        airports_prompt.telemetry_client = telemetry_client
        self._dialogs.add(airports_prompt)

        dates_prompt = DatesPrompt("dates_prompt", self._recognizer, telemetry_client=self.telemetry_client)
        dates_prompt.telemetry_client = telemetry_client
        self._dialogs.add(dates_prompt)

        budget_prompt = BudgetPrompt("budget_prompt", self._recognizer, telemetry_client= self.telemetry_client)
        budget_prompt.telemetry_client = telemetry_client
        self._dialogs.add(budget_prompt)

        confirm_prompt = ConfirmPrompt("validation_prompt", self.is_validated)
        confirm_prompt.telemetry_client = telemetry_client
        self._dialogs.add(confirm_prompt)

        waterfall_dialog = WaterfallDialog(
            "main_dialog",
            [self.airports, self.dates, self.budget, self.validation, self.completed],
        )
        waterfall_dialog.telemetry_client = telemetry_client
        self._dialogs.add(waterfall_dialog)

    async def airports(self, waterfall_step: WaterfallStepContext):
        await waterfall_step._turn_context.send_activity(
            f"Welcome to the flight booking bot. I was built to help you to book your round-trip ticket.\n I will ask you some informations to complete your request then i can proceed. I hope our interraction will going well ! "
        )
        return await waterfall_step.prompt(
            "airports_prompt",
            PromptOptions(
                prompt=MessageFactory.text(
                    f"First question; Where are the origin and the destination of your vacations? "
                )
            ),
        )

    async def dates(self, waterfall_step: WaterfallStepContext):
        entities_to_save = ["or_city", "dst_city"]
        await self._save_entities_values(waterfall_step, entities_to_save)
        return await waterfall_step.prompt(
            "dates_prompt",
            PromptOptions(
                prompt=MessageFactory.text(
                    f"Great ! Now please indicate your dates filghts ."
                )
            ),
        )

    async def budget(self, waterfall_step: WaterfallStepContext):
        entities_to_save = ["str_date", "end_date"]
        await self._save_entities_values(waterfall_step, entities_to_save)
        return await waterfall_step.prompt(
            "budget_prompt",
            PromptOptions(
                prompt=MessageFactory.text(
                    f"Awesome! I only need one more information . Can you tell me your maximum budget?"
                )
            ),
        )

    async def validation(self, waterfall_step: WaterfallStepContext):
        entities_to_save = ["budget"]
        await self._save_entities_values(waterfall_step, entities_to_save)

        or_city = waterfall_step.values["or_city"]
        dst_city = waterfall_step.values["dst_city"]
        str_date = waterfall_step.values["str_date"]
        end_date = waterfall_step.values["end_date"]
        budget = waterfall_step.values["budget"]

        message = f"Ok, let me summarize ! You want to book a plane from '{or_city}' to '{dst_city}', leaving '{str_date}' and coming back '{end_date}' with a budget of '{budget}'. Do you confirm these data? "
        # message = f'or_city : {or_city} ; dst_city : {dst_city} ; departure: {str_date} ; return : {end_date} ; budget : {budget}'
        return await waterfall_step.prompt(
            "validation_prompt", PromptOptions(prompt=MessageFactory.text(message))
        )

    async def completed(self, waterfall_step: WaterfallStepContext):
        self.telemetry_client.track_event("Completed")
        await waterfall_step._turn_context.send_activity(
            "Congratulations, your flights are now booked ! Type anything to book another seat on a plane."
        )
        return await waterfall_step.end_dialog()

    async def is_validated(self, prompt_valid):
        if prompt_valid.recognized.value == False:
            await prompt_valid.context.send_activity(
                "Why did you say no :( ? Please reload me to correctly book your plane !"
            )
            return False
        if prompt_valid.recognized.value == None:
            await prompt_valid.context.send_activity(
                'Your entry is not recognized. Please respond with "yes" or "no"'
            )
            return False
        return True

    async def _save_entities_values(
        self, waterfall_step: WaterfallStepContext, entities_to_save: List[str]
    ):
        luis_result = await self._recognizer.recognize(waterfall_step._turn_context)
        result = luis_result.properties["luisResult"]
        entities = result.entities
        for entity in entities_to_save:
            waterfall_step.values[entity] = get_entity_value(entities, entity)

