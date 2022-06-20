from unittest import result
from botbuilder.core import (
    ActivityHandler,
    TurnContext,
    UserState,
    MessageFactory,
    ConversationState,
    BotTelemetryClient,
)
from botbuilder.ai.luis import LuisApplication, LuisPredictionOptions, LuisRecognizer
from botbuilder.dialogs import (
    DialogSet,
    WaterfallDialog,
    WaterfallStepContext,
    DialogExtensions,
)
from botbuilder.dialogs.prompts import (
    TextPrompt,
    ConfirmPrompt,
    PromptOptions,
    PromptValidatorContext,
)
from typing import List
from config import DefaultConfig
from Prompts import AirportsPrompt, DatesPrompt, BudgetPrompt
from lib.FlightBookingRecognizer import FlightBookingRecognizer
from lib.BookingDialog import BookingDialog


class MyBot(ActivityHandler):
    def __init__(
        self,
        conversation: ConversationState,
        user_state: UserState,
        telemetry_client: BotTelemetryClient = None,
    ) -> None:
        self.LuisReg = FlightBookingRecognizer(telemetry_client)

        self.con_state = conversation
        self.user_state = user_state
        self.state_prop = self.con_state.create_property("dialog_set")
        self.dialog_set = DialogSet(self.state_prop)

        airports_prompt = AirportsPrompt("airports_prompt", self.LuisReg)
        airports_prompt.telemetry_client = telemetry_client

        dates_prompt = DatesPrompt("dates_prompt", self.LuisReg)
        dates_prompt.telemetry_client = telemetry_client

        budget_prompt = BudgetPrompt("budget_prompt", self.LuisReg)
        budget_prompt.telemetry_client = telemetry_client

        confirm_prompt = ConfirmPrompt("validation_prompt", self.is_validated)
        confirm_prompt.telemetry_client = telemetry_client

        waterfall_dialog = WaterfallDialog(
            "main_dialog",
            [self.airports, self.dates, self.budget, self.validation, self.completed],
        )
        waterfall_dialog.telemetry_client = telemetry_client
        self.dialog_set.add(airports_prompt)
        self.dialog_set.add(dates_prompt)
        self.dialog_set.add(budget_prompt)
        self.dialog_set.add(confirm_prompt)

        self.dialog_set.add(waterfall_dialog)
        self.dialog_set.telemetry_client = telemetry_client
        self.telemetry = telemetry_client

        # self.dialog = BookingDialog('main_dialog', telemetry_client, self.LuisReg)

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

    async def is_validated(self, prompt_valid: PromptValidatorContext):
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

    async def completed(self, waterfall_step: WaterfallStepContext):
        await waterfall_step._turn_context.send_activity(
            "Congratulations, your flights are now booked ! Type anything to book another seat on a plane."
        )
        return await waterfall_step.end_dialog()

    async def on_turn(self, turn_context: TurnContext):
        dialog_context = await self.dialog_set.create_context(turn_context)

        if dialog_context.active_dialog is not None:
            await dialog_context.continue_dialog()
        else:
            await dialog_context.begin_dialog("main_dialog")

        await self.con_state.save_changes(turn_context)

    def _get_entity_value(self, entities, key):
        for entity in entities:
            if entity.type == key:
                return entity.entity

    async def _save_entities_values(
        self, waterfall_step: WaterfallStepContext, entities_to_save: List[str]
    ):
        luis_result = await self.LuisReg.recognize(waterfall_step._turn_context)
        result = luis_result.properties["luisResult"]
        entities = result.entities
        for entity in entities_to_save:
            waterfall_step.values[entity] = self._get_entity_value(entities, entity)

    async def on_message_activity(self, turn_context: TurnContext):
        # await DialogExtensions.run_dialog(
        #     self.dialog,
        #     turn_context,
        #     self.con_state.create_property("DialogState"),
        # )

        # Save any state changes that might have occured during the turn.
        await self.conversation_state.save_changes(turn_context, False)
        await self.user_state.save_changes(turn_context, False)
