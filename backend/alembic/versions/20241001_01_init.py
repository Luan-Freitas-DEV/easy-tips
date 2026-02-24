"""init

Revision ID: 20241001_01
Revises:
Create Date: 2024-10-01
"""

from alembic import op
import sqlalchemy as sa


revision = "20241001_01"
down_revision = None
branch_labels = None
depends_on = None


user_role = sa.Enum("SHIPPER", "DRIVER", "BOTH", name="userrole")
service_status = sa.Enum(
    "PUBLICADO", "EM_NEGOCIACAO", "ACEITO", "COLETADO", "ENTREGUE", "CANCELADO", name="servicestatus"
)
offer_kind = sa.Enum("ACCEPT", "COUNTER", name="offerkind")
offer_status = sa.Enum("PENDING", "ACCEPTED", "REJECTED", name="offerstatus")


def upgrade() -> None:
    user_role.create(op.get_bind(), checkfirst=True)
    service_status.create(op.get_bind(), checkfirst=True)
    offer_kind.create(op.get_bind(), checkfirst=True)
    offer_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(120), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "driver_profiles",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("vehicle_type", sa.String(120), nullable=True),
        sa.Column("capacity_kg", sa.Float(), nullable=True),
        sa.Column("base_city", sa.String(120), nullable=True),
        sa.Column("base_state", sa.String(2), nullable=True),
    )
    op.create_table(
        "shipper_profiles",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("profile_type", sa.String(10), nullable=False),
        sa.Column("document_id", sa.String(30), nullable=True),
    )

    op.create_table(
        "services",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("created_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("service_type", sa.String(80), nullable=False),
        sa.Column("origin_address", sa.String(255), nullable=False),
        sa.Column("origin_lat", sa.Float(), nullable=False),
        sa.Column("origin_lng", sa.Float(), nullable=False),
        sa.Column("dest_address", sa.String(255), nullable=False),
        sa.Column("dest_lat", sa.Float(), nullable=False),
        sa.Column("dest_lng", sa.Float(), nullable=False),
        sa.Column("pickup_window_start", sa.DateTime(), nullable=False),
        sa.Column("pickup_window_end", sa.DateTime(), nullable=False),
        sa.Column("delivery_window_start", sa.DateTime(), nullable=False),
        sa.Column("delivery_window_end", sa.DateTime(), nullable=False),
        sa.Column("offered_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", service_status, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_services_created_by", "services", ["created_by_user_id"])

    op.create_table(
        "offers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("service_id", sa.Integer(), sa.ForeignKey("services.id"), nullable=False),
        sa.Column("driver_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("kind", offer_kind, nullable=False),
        sa.Column("price", sa.Numeric(12, 2), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("status", offer_status, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_offers_service_id", "offers", ["service_id"])

    op.create_table(
        "assignments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("service_id", sa.Integer(), sa.ForeignKey("services.id"), nullable=False, unique=True),
        sa.Column("driver_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("accepted_offer_id", sa.Integer(), sa.ForeignKey("offers.id"), nullable=False),
        sa.Column("accepted_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "driver_intents",
        sa.Column("driver_user_id", sa.Integer(), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("current_lat", sa.Float(), nullable=True),
        sa.Column("current_lng", sa.Float(), nullable=True),
        sa.Column("intended_dest_lat", sa.Float(), nullable=False),
        sa.Column("intended_dest_lng", sa.Float(), nullable=False),
        sa.Column("intended_dest_address", sa.String(255), nullable=False),
        sa.Column("available_from", sa.DateTime(), nullable=False),
        sa.Column("available_to", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("driver_intents")
    op.drop_table("assignments")
    op.drop_index("ix_offers_service_id", table_name="offers")
    op.drop_table("offers")
    op.drop_index("ix_services_created_by", table_name="services")
    op.drop_table("services")
    op.drop_table("shipper_profiles")
    op.drop_table("driver_profiles")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    offer_status.drop(op.get_bind(), checkfirst=True)
    offer_kind.drop(op.get_bind(), checkfirst=True)
    service_status.drop(op.get_bind(), checkfirst=True)
    user_role.drop(op.get_bind(), checkfirst=True)
