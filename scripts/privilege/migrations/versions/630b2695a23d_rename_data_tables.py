# type:ignore
"""rename data tables

Revision ID: 630b2695a23d
Revises: eb3530297398
Create Date: 2020-12-14 00:09:07.215044

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "630b2695a23d"
down_revision = "eb3530297398"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        "feature_data_privilege_fkey", "feature_data", type_="foreignkey"
    )
    op.drop_index("ix_feature_privileges_unique", table_name="feature_statuses")
    op.drop_index("ix_feature_statuses_group", table_name="feature_statuses")
    op.drop_index("ix_feature_statuses_privilege", table_name="feature_statuses")
    op.drop_index("ix_feature_statuses_user", table_name="feature_statuses")
    op.drop_table("feature_statuses")
    op.drop_index("ix_feature_privilege_name", table_name="feature_privilege")
    op.drop_index("ix_feature_privilege_parent", table_name="feature_privilege")
    op.drop_table("feature_privilege")
    op.create_table(
        "feature_list",
        sa.Column("pid", sa.Integer(), nullable=False),
        sa.Column("time", sa.DateTime(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("parent", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("pid"),
    )
    op.create_index(op.f("ix_feature_list_name"), "feature_list", ["name"], unique=True)
    op.create_index(
        op.f("ix_feature_list_parent"), "feature_list", ["parent"], unique=False
    )
    op.create_index(
        op.f("ix_feature_list_time"), "feature_list", ["time"], unique=False
    )
    op.create_table(
        "feature_privileges",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("group", sa.Integer(), nullable=True),
        sa.Column("user", sa.Integer(), nullable=False),
        sa.Column("privilege", sa.String(length=255), nullable=False),
        sa.Column("status", sa.SmallInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["privilege"],
            ["feature_list.name"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_feature_privileges_group"),
        "feature_privileges",
        ["group"],
        unique=False,
    )
    op.create_index(
        op.f("ix_feature_privileges_privilege"),
        "feature_privileges",
        ["privilege"],
        unique=False,
    )
    op.create_index(
        "ix_feature_privileges_unique",
        "feature_privileges",
        ["group", "user", "privilege"],
        unique=True,
    )
    op.create_index(
        op.f("ix_feature_privileges_user"), "feature_privileges", ["user"], unique=False
    )
    op.create_foreign_key(None, "feature_data", "feature_list", ["privilege"], ["name"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "feature_data", type_="foreignkey")
    op.create_foreign_key(
        "feature_data_privilege_fkey",
        "feature_data",
        "feature_privilege",
        ["privilege"],
        ["name"],
    )
    op.create_table(
        "feature_statuses",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("group", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("user", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column(
            "privilege", sa.VARCHAR(length=255), autoincrement=False, nullable=False
        ),
        sa.Column("status", sa.SMALLINT(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(
            ["privilege"],
            ["feature_privilege.name"],
            name="feature_statuses_privilege_fkey",
        ),
        sa.PrimaryKeyConstraint("id", name="feature_statuses_pkey"),
    )
    op.create_index(
        "ix_feature_statuses_user", "feature_statuses", ["user"], unique=False
    )
    op.create_index(
        "ix_feature_statuses_privilege", "feature_statuses", ["privilege"], unique=False
    )
    op.create_index(
        "ix_feature_statuses_group", "feature_statuses", ["group"], unique=False
    )
    op.create_index(
        "ix_feature_privileges_unique",
        "feature_statuses",
        ["group", "user", "privilege"],
        unique=True,
    )
    op.create_table(
        "feature_privilege",
        sa.Column("pid", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("name", sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column("parent", sa.VARCHAR(length=255), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("pid", name="feature_privilege_pkey"),
    )
    op.create_index(
        "ix_feature_privilege_parent", "feature_privilege", ["parent"], unique=False
    )
    op.create_index(
        "ix_feature_privilege_name", "feature_privilege", ["name"], unique=True
    )
    op.drop_index(op.f("ix_feature_privileges_user"), table_name="feature_privileges")
    op.drop_index("ix_feature_privileges_unique", table_name="feature_privileges")
    op.drop_index(
        op.f("ix_feature_privileges_privilege"), table_name="feature_privileges"
    )
    op.drop_index(op.f("ix_feature_privileges_group"), table_name="feature_privileges")
    op.drop_table("feature_privileges")
    op.drop_index(op.f("ix_feature_list_time"), table_name="feature_list")
    op.drop_index(op.f("ix_feature_list_parent"), table_name="feature_list")
    op.drop_index(op.f("ix_feature_list_name"), table_name="feature_list")
    op.drop_table("feature_list")
    # ### end Alembic commands ###
