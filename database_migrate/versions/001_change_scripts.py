from sqlalchemy import Table, Column, Integer, String, MetaData

meta = MetaData()

account = Table(
    'account', meta,
    Column('id', Integer, primary_key=True),
    Column('login', String(40)),
    Column('passwd', String(40)),
)


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    account.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    account.drop()
