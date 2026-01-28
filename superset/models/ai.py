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
from __future__ import annotations

import logging
from typing import Any, Optional

from flask_appbuilder import Model
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, select
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from superset import security_manager
from superset.extensions import encrypted_field_factory
from superset.models.helpers import AuditMixinNullable

logger = logging.getLogger(__name__)


class AIProviderConfig(AuditMixinNullable, Model):
    """
    Configuration for AI Providers (OpenAI, Gemini, etc.)
    """

    __tablename__ = "ai_provider_config"

    id = Column(Integer, primary_key=True)
    provider = Column(String(50), nullable=False, unique=True)  # e.g., 'openai', 'gemini'
    api_key = Column(encrypted_field_factory.create(String(1024)), nullable=False)
    model_name = Column(String(100), nullable=False)  # e.g., 'gpt-4', 'gemini-pro'
    is_active = Column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"{self.provider} ({self.model_name})"


class AIChatLog(Model):
    """
    Log of AI Chat interactions for context and auditing.
    """

    __tablename__ = "ai_chat_log"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("ab_user.id"), nullable=False)
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"), nullable=False)
    prompt = Column(Text, nullable=False)
    response_sql = Column(Text, nullable=True)
    response_text = Column(Text, nullable=True)
    timestamp = Column(DateTime, nullable=False)

    user = relationship(security_manager.user_model, foreign_keys=[user_id])
    dashboard = relationship("Dashboard", foreign_keys=[dashboard_id])

    @hybrid_property
    def user_name(self) -> str:
        if self.user:
            return f"{self.user.first_name} {self.user.last_name}".strip()
        return ""

    @user_name.expression
    def user_name(cls) -> Any:  # type: ignore
        # Concatenate first_name and last_name with a space
        return select([
            security_manager.user_model.first_name + " " + security_manager.user_model.last_name
        ]).where(
            security_manager.user_model.id == cls.user_id
        ).label("user_name")

    @hybrid_property
    def dashboard_title(self) -> str:
        return self.dashboard.dashboard_title if self.dashboard else ""

    @dashboard_title.expression
    def dashboard_title(cls) -> Any:  # type: ignore
        from superset.models.dashboard import Dashboard
        return select([Dashboard.dashboard_title]).where(
            Dashboard.id == cls.dashboard_id
        ).label("dashboard_title")

    def __repr__(self) -> str:
        return f"AIChatLog(user_id={self.user_id}, dashboard_id={self.dashboard_id})"
