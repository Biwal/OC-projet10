from unittest.mock import Base
from botbuilder.dialogs.prompts import Prompt, PromptOptions,PromptRecognizerResult
from botbuilder.core.turn_context import TurnContext
from botbuilder.schema import ActivityTypes
from botbuilder.ai.luis import LuisRecognizer
from recognizers_text import Culture

from typing import Dict, List
from abc import abstractmethod

class BasePrompt (Prompt):
    def __init__(self, 
        dialog_id,
        luis_reg: LuisRecognizer,
        validator : object = None,
        defaultLocale = None):
     super().__init__(dialog_id, validator=validator)
     
     if defaultLocale is None:
        defaultLocale = Culture.English

     self._defaultLocale = defaultLocale
     self._luis_reg = luis_reg

    async def on_prompt(
        self, 
        turn_context: TurnContext, 
        state: Dict[str, object], 
        options: PromptOptions, 
        is_retry: bool, 
    ):
        if not turn_context:
            raise TypeError("turn_context Can’t  be none")
        if not options:
            raise TypeError("options Can’t  be none")

        if is_retry and options.retry_prompt is not None:
            await turn_context.send_activity(options.retry_prompt)
        else:
            if options.prompt is not None:
                await turn_context.send_activity(options.prompt)    

    async def on_recognize(self,
        turn_context: TurnContext, 
        state: Dict[str, object], 
        options: PromptOptions, 
    ) -> PromptRecognizerResult:  
        if not turn_context:
            raise TypeError("turn_context cannt be none")
        if turn_context.activity.type == ActivityTypes.message:
            usertext = turn_context.activity.text
        turn_context.activity.locale = self._defaultLocale
        prompt_result = await self.validate(turn_context)
        return prompt_result
    
    @abstractmethod
    async def validate(self, userText, turn_context)->PromptRecognizerResult:
        ...
        
    def _get_entity_value(self, entities, key):
        for entity in  entities:
            if entity.type == key:
                return entity.entity
            
    async def _validator(self, turn_context: TurnContext, valid_entities: List[str], error_message:str):
        prompt_result = PromptRecognizerResult()
        
        luis_result = await self._luis_reg.recognize(turn_context)
        result = luis_result.properties["luisResult"]
        entities_type = [entity.type for entity in result.entities]
        
        if all([valid_entity in entities_type for valid_entity in valid_entities]):
            prompt_result.succeeded = True
        else:
            await turn_context.send_activity(error_message)
        return prompt_result
        

    
class AirportsPrompt(BasePrompt):
    def __init__(self, dialog_id, luis_reg: LuisRecognizer, validator: object = None, defaultLocale=None):
        super().__init__(dialog_id, luis_reg, validator, defaultLocale)
        
    async def validate(self,  turn_context:TurnContext) -> PromptRecognizerResult:
        valid_entities = ['or_city', 'dst_city']    
        error_message="I'm sorry I don't understand the departure and/or the arrival city. Could you please re-write your informations?"
        return await super()._validator(turn_context,valid_entities, error_message)
    
    
class DatesPrompt(BasePrompt):
    def __init__(self, dialog_id, luis_reg: LuisRecognizer, validator: object = None, defaultLocale=None):
        super().__init__(dialog_id, luis_reg, validator, defaultLocale)
        
    async def validate(self, turn_context) -> PromptRecognizerResult:
        valid_entities = ['str_date', 'end_date']
        error_message= "I'm sorry I don't understad your preferences for the dates flight. Could you please reformulate your sentence?"
        return await super()._validator(turn_context, valid_entities, error_message)
    
    
class BudgetPrompt(BasePrompt):
    def __init__(self, dialog_id, luis_reg: LuisRecognizer, validator: object = None, defaultLocale=None):
        super().__init__(dialog_id, luis_reg, validator, defaultLocale)
        
    async def validate(self, turn_context) -> PromptRecognizerResult:
        valid_entities = ['budget']    
        error_message="I'm sorry I don't understand your budget for this travel. Could you type it again?"
        return await super()._validator(turn_context, valid_entities, error_message)
        