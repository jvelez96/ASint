class Building:
    def __init__(self, new_id, new_name, toplevel_id, latitude, longitude, radius):
        self.id = new_id
        self.name = new_name
        self.toplevel_id = toplevel_id
        self.latitude = latitude
        self.longitude = longitude
        self.radius = radius

    def get_building(self):
        return self

    def set_building(self, new_id, new_name, toplevel_id, latitude, longitude, radius):
        if new_id is not None:
            self.id = new_id
        if new_name is not None:
            self.name = new_name
        if toplevel_id is not None:
            self.toplevel_id = toplevel_id
        if latitude is not None:
            self.latitude = latitude
        if longitude is not None:
            self.longitude = longitude
        if radius is not None:
            self.radius = radius
        return 1