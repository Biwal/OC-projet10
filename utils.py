def get_entity_value( entities, key):
    for entity in entities:
        if entity.type == key:
            return entity.entity
        
        
def check_all_entities_in(valid_entities, entities_to_check):
    entities_type = [entity.type for entity in entities_to_check]

    if all([valid_entity in entities_type for valid_entity in valid_entities]):
        return True
    return False