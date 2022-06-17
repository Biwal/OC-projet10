import sys
import pathlib
import pytest
import aiounittest
from botbuilder.ai.luis import LuisApplication, LuisPredictionOptions, LuisRecognizer
# from Prompts import BudgetPrompt
# from config import DefaultConfig 
import asyncio
# current = pathlib.Path(__file__).parent.parent
# libpath = current.joinpath("C:\\Openclassroom\\OC-projet10")
# sys.path.append(str(libpath))

from botbuilder.dialogs.prompts import (
    AttachmentPrompt, 
    PromptOptions, 
    PromptValidatorContext, 
)

from botbuilder.core import (
    TurnContext, 
    ConversationState, 
    MemoryStorage, 
    MessageFactory, 
)
from botbuilder.schema import Activity, ActivityTypes, Attachment
from botbuilder.dialogs import DialogSet, DialogTurnStatus
from botbuilder.core.adapters import TestAdapter
# from Prompts import  AirportsPrompt, DatesPrompt, BudgetPrompt
from unittest.mock import Base
from botbuilder.dialogs.prompts import Prompt, PromptOptions,PromptRecognizerResult
from botbuilder.core.turn_context import TurnContext
from botbuilder.schema import ActivityTypes
from botbuilder.ai.luis import LuisRecognizer
from recognizers_text import Culture

from typing import Coroutine, Dict, List
from abc import abstractmethod
#!/usr/bin/env python3

# class DefaultConfig:
#     """ Bot Configuration """

#     PORT = 3978
#     APP_ID = "467e16ca-6676-44f5-af22-de70745ee8da"
#     APP_PASSWORD = "nIx8Q~vZnaMMhbOztpFT.jdLwJNqqOcEXBD55dvP"
#     LUIS_ID = "28f58886-4988-435b-8749-032ad1e3009c"
#     LUIS_KEY = "47cd37fc73fa430481dcfd3f48a39d76"
#     BOT_URL = "https://botluisocprojet10.cognitiveservices.azure.com/"
#     APP_INSIGHT_KEY = "3e7e3d0d-f7bb-497b-b60c-f5695a907970"
    
    
 
# class BasePrompt (Prompt):
#     def __init__(self, 
#         dialog_id,
#         luis_reg: LuisRecognizer,
#         validator : object = None,
#         defaultLocale = None):
#      super().__init__(dialog_id, validator=validator)
     
#      if defaultLocale is None:
#         defaultLocale = Culture.English

#      self._defaultLocale = defaultLocale
#      self._luis_reg = luis_reg

#     async def on_prompt(
#         self, 
#         turn_context: TurnContext, 
#         state: Dict[str, object], 
#         options: PromptOptions, 
#         is_retry: bool, 
#     ):
#         if not turn_context:
#             raise TypeError("turn_context Can’t  be none")
#         if not options:
#             raise TypeError("options Can’t  be none")

#         if is_retry and options.retry_prompt is not None:
#             await turn_context.send_activity(options.retry_prompt)
#         else:
#             if options.prompt is not None:
#                 await turn_context.send_activity(options.prompt)    

#     async def on_recognize(self,
#         turn_context: TurnContext, 
#         state: Dict[str, object], 
#         options: PromptOptions, 
#     ) -> PromptRecognizerResult:  
#         if not turn_context:
#             raise TypeError("turn_context cannt be none")
#         if turn_context.activity.type == ActivityTypes.message:
#             usertext = turn_context.activity.text
#         turn_context.activity.locale = self._defaultLocale
#         prompt_result = await self.validate(turn_context)
#         return prompt_result
    
#     @abstractmethod
#     async def validate(self, userText, turn_context)->PromptRecognizerResult:
#         ...
        
#     def _get_entity_value(self, entities, key):
#         for entity in  entities:
#             if entity.type == key:
#                 return entity.entity
            
#     async def _validator(self, turn_context: TurnContext, valid_entities: List[str], error_message:str):
#         prompt_result = PromptRecognizerResult()
        
#         luis_result = await self._luis_reg.recognize(turn_context)
#         result = luis_result.properties["luisResult"]
#         entities_type = [entity.type for entity in result.entities]
        
#         if all([valid_entity in entities_type for valid_entity in valid_entities]):
#             prompt_result.succeeded = True
#         else:
#             await turn_context.send_activity(error_message)
#         return prompt_result
        

    
# class AirportsPrompt(BasePrompt):
#     def __init__(self, dialog_id, luis_reg: LuisRecognizer, validator: object = None, defaultLocale=None):
#         super().__init__(dialog_id, luis_reg, validator, defaultLocale)
        
#     async def validate(self,  turn_context:TurnContext) -> PromptRecognizerResult:
#         valid_entities = ['or_city', 'dst_city']    
#         error_message="I'm sorry I don't understand the departure and/or the arrival city. Could you please re-write your informations?"
#         return await super()._validator(turn_context,valid_entities, error_message)
    
    
# class DatesPrompt(BasePrompt):
#     def __init__(self, dialog_id, luis_reg: LuisRecognizer, validator: object = None, defaultLocale=None):
#         super().__init__(dialog_id, luis_reg, validator, defaultLocale)
        
#     async def validate(self, turn_context) -> PromptRecognizerResult:
#         valid_entities = ['str_date', 'end_date']
#         error_message= "I'm sorry I don't understad your preferences for the dates flight. Could you please reformulate your sentence?"
#         return await super()._validator(turn_context, valid_entities, error_message)
    
    
# class BudgetPrompt(BasePrompt):
#     def __init__(self, dialog_id, luis_reg: LuisRecognizer, validator: object = None, defaultLocale=None):
#         super().__init__(dialog_id, luis_reg, validator, defaultLocale)
        
#     async def validate(self, turn_context) -> PromptRecognizerResult:
#         valid_entities = ['budget']    
#         error_message="I'm sorry I don't understand your budget for this travel. Could you type it again?"
#         return await super()._validator(turn_context, valid_entities, error_message)
        
# class BudgetPromptTest(aiounittest.AsyncTestCase):
#     async def test_budget_prompt(self):
#         async def exec_test(turn_context:TurnContext)->Coroutine:
#             dialog_context = await dialogs.create_context(turn_context)

#             results = await dialog_context.continue_dialog()
#             if (results.status == DialogTurnStatus.Empty):
#                 options = PromptOptions(
#                     prompt = Activity(
#                         type = ActivityTypes.message, 
#                         text = "Awesome! I only need one more information . Can you tell me your maximum budget?"
#                         )
#                     )
#                 await dialog_context.prompt("budget_prompt", options)

#             elif results.status == DialogTurnStatus.Complete:
#                 reply = results.result
#                 await turn_context.send_activity(reply)

#             await conv_state.save_changes(turn_context)

#         CONFIG = DefaultConfig()
        
#         luis_app = LuisApplication(CONFIG.LUIS_ID, CONFIG.LUIS_KEY, CONFIG.BOT_URL)
#         luis_option = LuisPredictionOptions(include_all_intents=True, include_instance_data=True)
#         LuisReg = LuisRecognizer(luis_app, luis_option, True)
#         adapter = TestAdapter(exec_test)

#         conv_state = ConversationState(MemoryStorage())

#         dialogs_state = conv_state.create_property("dialog-state")
#         dialogs = DialogSet(dialogs_state)
#         dialogs.add(BudgetPrompt("budget_prompt",LuisReg ))

#         step1 = await adapter.test('Hello', 'Awesome! I only need one more information . Can you tell me your maximum budget?')
#         step2 = await step1.send("i can't spend more than 234€")
#         # st = await step1.send():
#         # await step2.assert_reply("234 €")
#         assert 4==4
        
def test_test():
    assert (2*2) == 4