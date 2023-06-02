class Entities:
    def __init__(self):
        self.players_backend = []
        self.bullets_backend = []
        self.frontend_entities = {"players": [], "bullets": []}

    def add(self, entity_type, entity):
        if entity_type == "player":
            self.players_backend.append(entity)
            self.frontend_entities["players"].append(entity['info'])

        elif entity_type == "bullet":
            entity['id'] = len(self.bullets_backend)
            self.bullets_backend.append(entity)
            self.frontend_entities["bullets"].append(entity['info'])
    
    def remove_entity(self, entity_type, entity):
        if entity_type == "player":
            self.players_backend.remove(entity)
            self.frontend_entities["players"].remove(entity['info'])

        elif entity_type == "bullet":
            self.bullets_backend.remove(entity)
            self.frontend_entities["bullets"].remove(entity['info'])

    # def remove_entity_by_id(self, entity_type, id):
    #     if entity_type == "player":
    #         player = next((p for p in self.players_backend if p['id'] == id), None)
    #         if player is not None:
    #             self.players_backend.remove(player)
    #             self.frontend_entities["players"].remove(player['info'])

    #     elif entity_type == "bullet":
    #         bullet = next((b for b in self.bullets_backend if b['id'] == id), None)
    #         if bullet is not None:
    #             self.bullets_backend.remove(bullet)
    #             self.frontend_entities["bullets"].remove(bullet['info'])