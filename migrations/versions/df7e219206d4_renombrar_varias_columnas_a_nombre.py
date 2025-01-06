"""renombrar varias columnas a nombre

Revision ID: df7e219206d4
Revises: 8da1ba3e178c
Create Date: 2025-01-06 12:26:52.210075

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'df7e219206d4'
down_revision = '8da1ba3e178c'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('actividades', 'actividad', new_column_name='nombre')
    op.alter_column('dias', 'dia', new_column_name='nombre')
    op.alter_column('responsables', 'responsable', new_column_name='nombre')
    op.alter_column('tareas', 'tarea', new_column_name='nombre')

