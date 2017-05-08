from sqlalchemy import Column, BIGINT, String

from meetup_facebook_bot.models.base import Base


class Speaker(Base):
    __tablename__ = 'speakers'
    facebook_id = Column(BIGINT, primary_key=True)
    name = Column(String(128), nullable=False)

    def __repr__(self):
        return '<Speaker %r>' % self.facebook_id
