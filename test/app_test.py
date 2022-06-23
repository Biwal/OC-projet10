from utils import get_entity_value, check_all_entities_in
from FlightBookingRecognizer import FlightBookingRecognizer
from botbuilder.ai.luis import LuisRecognizer

class MockEntity:
    def __init__(self, typ: str, entity: str) -> None:
        self.type = typ
        self.entity = entity

def test_get_entity_value():
    entities = [MockEntity("un", "1"), MockEntity("deux", "2")]
    key = "un"

    res = get_entity_value(entities, key)
    assert res == "1"

def test_check_all_entities_in():
    entities = [
        MockEntity("un", "1"),
        MockEntity("deux", "2"),
        MockEntity("trois", "3"),
        MockEntity("quatre", "4"),
    ]
    valid_entities = ["deux", "trois"]

    res = check_all_entities_in(valid_entities, entities)
    assert res == True

    valid_entities = ["deux", "cinq"]
    res = check_all_entities_in(valid_entities, entities)
    assert res == False

def test_FlightBookingRecognizer_instance():
    fbr = FlightBookingRecognizer()
    assert isinstance(fbr._recognizer, LuisRecognizer)
