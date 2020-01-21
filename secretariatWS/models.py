from main import db
from datetime import datetime
from flask import url_for

class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items':[item.to_dict() for item in resources.items],
            '_meta' : {
                'page' : page,
                'per_page' : per_page,
                'total_pages' : resources.pages,
                'total_items' : resources.total,
            },
            '_links' : {
                'self': url_for(endpoint, page=page, per_page=per_page, **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data

class Secretariat (PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True)
    location = db.Column(db.String(120), index=True)
    description = db.Column(db.String(300))
    opening_hours = db.Column(db.String(120))

    def to_dict(self):
        data = {
            'id' : self.id,
            'name' : self.name,
            'location' : self.location,
            'description' : self.description,
            'opening_hours' : self.opening_hours,
        }
        return data

    def from_dict(self, data, new_secretariat = False):
        for field in ['name', 'location', 'description', 'opening_hours']:
            if field in data:
                setattr(self, field, data[field])


    def __repr__(self):
        return '<Secretariat Name {}>'.format(self.name)


