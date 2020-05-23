
class ApiResource():
    def as_dict(self, db_session = None):
        ret = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return ret
