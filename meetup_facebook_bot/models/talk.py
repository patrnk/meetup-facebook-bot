from sqlalchemy import Column, Integer, String, BIGINT, ForeignKey
from sqlalchemy.orm import relationship

from meetup_facebook_bot.models.base import Base
from meetup_facebook_bot.models.speaker import Speaker  # noqa
from meetup_facebook_bot.models.like import Like


class Talk(Base):
    __tablename__ = 'talks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(128), unique=True, nullable=False)
    description = Column(String(512))
    speaker_facebook_id = Column(
        BIGINT,
        ForeignKey('speakers.facebook_id'),
        nullable=False
    )

    speaker = relationship('Speaker')
    likes = relationship('Like')

    def is_liked_by(self, user_id, db_session):
        like = db_session.query(Like).filter_by(
            user_facebook_id=user_id,
            talk_id=self.id
        )
        return db_session.query(like.exists()).scalar()

    def count_likes(self, db_session):
        return db_session.query(Like).filter_by(talk_id=self.id).count()

    def set_like(self, user_id, db_session):
        if self.is_liked_by(user_id, db_session):
            raise ValueError('The like has already been set.')
        like = Like(user_facebook_id=user_id, talk_id=self.id)
        db_session.add(like)
        db_session.commit()

    def unset_like(self, user_id, db_session):
        if not self.is_liked_by(user_id, db_session):
            raise ValueError('The like has not been set.')
        like = db_session.query(Like).filter_by(
            user_facebook_id=user_id,
            talk_id=self.id
        ).scalar()
        db_session.delete(like)
        db_session.commit()

    def revert_like(self, user_id, db_session):
        if self.is_liked_by(user_id, db_session):
            self.unset_like(user_id, db_session)
        else:
            self.set_like(user_id, db_session)

    def __repr__(self):
        return '<Talk %r>' % self.id
