from uuid import UUID


def get_notify_channel_name(*, voxpop_id: UUID) -> str:
    if isinstance(voxpop_id, str):
        voxpop_id = UUID(voxpop_id)
    return f"questions_{voxpop_id.hex}"
