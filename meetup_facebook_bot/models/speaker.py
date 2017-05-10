from sqlalchemy import Column, BIGINT, String, Integer

from meetup_facebook_bot.models.base import Base


class Speaker(Base):
    __tablename__ = 'speakers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    page_scoped_id = Column(BIGINT)
    name = Column(String(128), nullable=False)
    token = Column(String(128), unique=True, nullable=False)

    def __repr__(self):
        return '<Speaker %r>' % self.id
