# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from unittest import result
from botbuilder.core import ActivityHandler, TurnContext, RecognizerResult, MessageFactory, ConversationState
from botbuilder.schema import ChannelAccount
from botbuilder.ai.luis import LuisApplication, LuisPredictionOptions, LuisRecognizer
from botbuilder.dialogs import DialogSet,WaterfallDialog,WaterfallStepContext
from botbuilder.dialogs.prompts import TextPrompt,NumberPrompt,PromptOptions,PromptValidatorContext


class MyBot(ActivityHandler):
    def __init__(self, conversation: ConversationState) -> None:
        luis_app = LuisApplication("28f58886-4988-435b-8749-032ad1e3009c","47cd37fc73fa430481dcfd3f48a39d76","https://botluisocprojet10.cognitiveservices.azure.com/")
        luis_option = LuisPredictionOptions(include_all_intents=True, include_instance_data=True)
        self.LuisReg = LuisRecognizer(luis_app, luis_option, True)
    # See https://aka.ms/about-bot-activity-message to learn more about the message and other activity types.
        self.con_statea = conversation
        self.state_prop = self.con_statea.create_property("dialog_set")
        self.dialog_set = DialogSet(self.state_prop)
        self.dialog_set.add(TextPrompt("text_prompt"))
        self.dialog_set.add(NumberPrompt("number_prompt",self.IsValidMobileNumber))
        
        self.dialog_set.add(WaterfallDialog("main_dialog",[self.introduce, self.airports]))



    async def introduce(self, waterfall_step : WaterfallStepContext):
        
        return await waterfall_step.prompt("text_prompt",PromptOptions(prompt=MessageFactory.text(f"Where do you want to move sir?")))

    async def airports(self, waterfall_step :WaterfallStepContext):
        mobile = waterfall_step._turn_context.activity.text
        waterfall_step.values["mobile"] = mobile
        luis_result = await self.LuisReg.recognize(waterfall_step._turn_context)
        intent = LuisRecognizer.top_intent(luis_result)
        # await waterfall_step.send_activity(f"Top Intent : {intent}")
        result = luis_result.properties["luisResult"]
        for e in result.entities:
            await waterfall_step._turn_context.send_activity(f"{e}")
        
        return await waterfall_step.prompt("text_prompt",PromptOptions(prompt=MessageFactory.text(f" Luis Result {result.entities[0].type}")))
        # waterfall_step.send_activity()


    async def IsValidMobileNumber(self,prompt_valid:PromptValidatorContext):
        if(prompt_valid.recognized.succeeded is False):
            await prompt_valid.context.send_activity("Hey please enter the number")
            return False
        else:
            value = str(prompt_valid.recognized.value)
            if len(value) < 3:
                await prompt_valid.context.send_activity("Please enter the valid mobile number")
                return False
        return True
    
        
    async def Completed(self,waterfall_step:WaterfallStepContext):
        email = waterfall_step._turn_context.activity.text
        waterfall_step.values["email"] = email
        name = waterfall_step.values["name"]
        mobile = waterfall_step.values["mobile"]
        mail = waterfall_step.values["email"] 
        profileinfo = f"name : {name} , Email : {mail} , mobile {mobile}"
        await waterfall_step._turn_context.send_activity(profileinfo)
        return await waterfall_step.end_dialog()
        
    async def on_turn(self,turn_context:TurnContext):
        dialog_context = await self.dialog_set.create_context(turn_context)

        if(dialog_context.active_dialog is not None):
            await dialog_context.continue_dialog()
        else:
            await dialog_context.begin_dialog("main_dialog")
        
        await self.con_statea.save_changes(turn_context)
