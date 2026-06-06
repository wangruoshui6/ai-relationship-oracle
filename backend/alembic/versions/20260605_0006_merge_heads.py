"""merge evaluation and calendar profile heads

Revision ID: 20260605_0006
Revises: 1698935c90e5, 20260605_0005
Create Date: 2026-06-05 14:10:00
"""

from typing import Sequence, Union


revision: str = "20260605_0006"
down_revision: Union[str, tuple[str, str], None] = ("1698935c90e5", "20260605_0005")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
