"""Index existing realtime text bodies without deleting any original messages."""
import hashlib

from alembic import op
from sqlalchemy import select

from app.models.exact_dedup import fingerprints
from app.models.schema_v1 import messages

revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    fingerprints.create(connection)
    query = select(messages.c.id, messages.c.content).where(messages.c.source.in_(('ocr', 'uia')))
    for batch in connection.execute(query).mappings().partitions(500):
        connection.execute(fingerprints.insert(), [dict(message_id=row['id'],
            body_hash=hashlib.sha256(row['content'].encode('utf-8')).hexdigest()) for row in batch])


def downgrade():
    fingerprints.drop(op.get_bind())
