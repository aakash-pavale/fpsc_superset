# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""add_ai_models

Revision ID: acba9b26ff1a
Revises: 9787190b3d89
Create Date: 2026-01-27 13:47:13.833582

"""

# revision identifiers, used by Alembic.
revision = 'acba9b26ff1a'
down_revision = '9787190b3d89'

from alembic import op
import sqlalchemy as sa
import superset

def upgrade():
    # Only create the new tables for AI Chat
    op.create_table('ai_provider_config',
        sa.Column('created_on', sa.DateTime(), nullable=True),
        sa.Column('changed_on', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('api_key', superset.utils.encrypt.EncryptedType(), nullable=False),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_by_fk', sa.Integer(), nullable=True),
        sa.Column('changed_by_fk', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['changed_by_fk'], ['ab_user.id'], ),
        sa.ForeignKeyConstraint(['created_by_fk'], ['ab_user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider')
    )
    op.create_table('ai_chat_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('dashboard_id', sa.Integer(), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('response_sql', sa.Text(), nullable=True),
        sa.Column('response_text', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['dashboard_id'], ['dashboards.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['ab_user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('ai_chat_log')
    op.drop_table('ai_provider_config')
