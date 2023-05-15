from uuid import UUID

import psycopg
from django.db import connection


def get_notify_channel_name(*, voxpop_id: UUID) -> str:
    if isinstance(voxpop_id, str):
        voxpop_id = UUID(voxpop_id)
    return f"questions_{voxpop_id.hex}"


def notify(*, channel_name: str, payload: str):
    conn = psycopg.connect(
        **connection.get_connection_params(),
        autocommit=True,
    )
    with conn.cursor() as cursor:
        cursor.execute(
            f"NOTIFY {channel_name}, '{payload}'",
        )
