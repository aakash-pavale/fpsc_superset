from typing import Any

from flask import g, request, Response
from flask_appbuilder.api import expose, protect, safe
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.models.sqla.filters import FilterContains, FilterStartsWith
from marshmallow import Schema, fields, validate

from superset import security_manager, db
from superset.models.ai import AIChatLog, AIProviderConfig
from superset.models.dashboard import Dashboard
from superset.views.base_api import BaseSupersetModelRestApi, statsd_metrics
from superset.exceptions import SupersetSecurityException

import logging
logger = logging.getLogger(__name__)

class AIChatQuerySchema(Schema):
    dashboard_id = fields.Integer(required=True)
    prompt = fields.String(required=True, validate=validate.Length(min=1))

class AIChatResponseSchema(Schema):
    response = fields.String()
    sql_query = fields.String()


class AIProviderRestApi(BaseSupersetModelRestApi):
    datamodel = SQLAInterface(AIProviderConfig)
    resource_name = "ai_provider"
    class_permission_name = "AIProvider"
    allow_browser_login = True
    list_columns = [
        "id",
        "provider",
        "api_key",
        "model_name",
        "is_active",
        "created_on",
        "changed_on",
        "changed_by.first_name",
        "changed_by.last_name",
    ]
    show_columns = list_columns
    search_columns = ["provider", "model_name"]
    add_columns = ["provider", "api_key", "model_name", "is_active"]
    edit_columns = add_columns


class AIChatRestApi(BaseSupersetModelRestApi):
    datamodel = SQLAInterface(AIChatLog)
    include_route_methods = {"get_list", "get", "info", "related", "delete", "post", "query"}
    resource_name = "ai_chat"
    class_permission_name = "AIChat"
    method_permission_name = {
        "query": "write",
        "get_list": "read",
        "get": "read",
        "info": "read",
        "post": "write",
        "delete": "write",
    }
    allow_browser_login = True

    list_columns = [
        "id",
        "user_name",
        "dashboard_title",
        "prompt",
        "response_text",
        "response_sql",
        "timestamp",
    ]
    show_columns = list_columns

    search_columns = ["prompt", "response_text", "user_name", "dashboard_title"]

    # search_filters = {
    #     "user_name": [FilterContains, FilterStartsWith],
    #     "dashboard_title": [FilterContains, FilterStartsWith],
    # }

    order_columns = ["timestamp", "prompt", "user_name", "dashboard_title"]

    # related_field_filters remove
    # order_rel_fields remove

    apispec_parameter_schemas = {
        "AIChatQuerySchema": AIChatQuerySchema,
    }
    openapi_spec_component_schemas = (
        AIChatQuerySchema,
        AIChatResponseSchema,
    )

    @expose("/query", methods=("POST",))
    @protect()
    @safe
    @statsd_metrics
    def query(self) -> Response:
        """AI Chat Query endpoint
        ---
        post:
          summary: Process AI Chat Query
          requestBody:
            required: true
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/AIChatQuerySchema'
          responses:
            200:
              description: AI Response
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/AIChatResponseSchema'
            400:
              $ref: '#/components/responses/400'
            401:
              $ref: '#/components/responses/401'
            403:
              $ref: '#/components/responses/403'
            500:
              $ref: '#/components/responses/500'
        """
        if not request.is_json:
            return self.response_400(message="Request is not JSON")

        try:
            data = AIChatQuerySchema().load(request.json)
        except Exception as err:
            return self.response_400(message=str(err))

        dashboard_id = data["dashboard_id"]
        prompt = data["prompt"]

        # 1. Check Dashboard Access
        try:
            # This is a broad check, refine as needed or fetch dashboard first
            dashboard = db.session.query(Dashboard).filter_by(id=dashboard_id).one_or_none()
            if not dashboard:
                return self.response_404()

            dashboard.raise_for_access()
        except SupersetSecurityException as ex:
            return self.response(403, message=str(ex))

        # 2. Gather Context (RLS, Schemas)
        from superset.ai_lab.llm import LLMClient
        llm_client = LLMClient()

        if not llm_client.is_configured():
             return self.response(400, message="AI Provider is not configured.")

        # Build Schema & RLS Context
        schema_context = []
        for datasource in dashboard.datasources:
            table_name = datasource.table_name if hasattr(datasource, 'table_name') else str(datasource)
            columns = [col.column_name for col in datasource.columns]

            # RLS Filters
            # security_manager.get_rls_filters returns a list of filters (typically objects with a 'clause' attribute)
            rls_filters = security_manager.get_rls_filters(datasource)
            rls_clauses = [f.clause for f in rls_filters]

            context_str = f"Table: {table_name}\nColumns: {', '.join(columns)}"
            if rls_clauses:
                context_str += f"\nRLS Constraints (MUST APPLY): {'; '.join(rls_clauses)}"
            schema_context.append(context_str)

        full_schema_context = "\n\n".join(schema_context)

        import pandas as pd

        system_prompt = (
            "You are a Superset Data Assistant. You have access to the following tables:\n\n"
            f"{full_schema_context}\n\n"
            "Security Context:\n"
            "You must assume the RLS Constraints listed above apply to the data. "
            "If generating SQL, you MUST include these constraints in the WHERE clause.\n\n"
            "Response Format:\n"
            "If the user asks for data (e.g. 'how many', 'total revenue'), return ONLY the SQL query inside a markdown block using '```sql'. "
            "Do NOT provide warnings about RLS.\n"
            "If the user asks for schema info, just explain in text."
        )

        try:
            ai_response = llm_client.query(system_prompt=system_prompt, user_prompt=prompt)
        except Exception as e:
             logger.error(f"AI Query Failed: {e}")
             return self.response(500, message=f"AI Error: {str(e)}")

        response_text = ai_response.get("response", "No response text.")
        response_sql = ai_response.get("sql_query")

        # 4. Execute SQL if present
        query_result = None
        if response_sql:
            try:
                # Find the database to execute against (using the first datasource as proxy)
                # In robust impl, we parse table name or allow LLM to specify db, but usually dashboard is single-db
                if dashboard.datasources:
                    datasource = list(dashboard.datasources)[0]
                    database = datasource.database

                    # Execute
                    # Use pandas for easy tabular formatting
                    with database.get_sqla_engine() as engine:
                        df = pd.read_sql_query(response_sql, engine)

                    # Convert to string/markdown table
                    if not df.empty:
                        query_result = df.to_markdown(index=False)
                        response_text += f"\n\n**Result:**\n{query_result}"
                    else:
                        response_text += "\n\n**Result:** No data found."
            except Exception as e:
                logger.error(f"SQL Execution Failed: {e}")
                response_text += f"\n\n**Error executing query:** {str(e)}"

        # 3. Log Interaction
        chat_log = AIChatLog(
            user_id=g.user.id,
            dashboard_id=dashboard_id,
            prompt=prompt,
            response_text=response_text,
            response_sql=response_sql,
            timestamp=db.func.now(),
        )
        db.session.add(chat_log)
        db.session.commit()

        return self.response(200, result={
            "response": response_text,
            "sql_query": response_sql
        })
