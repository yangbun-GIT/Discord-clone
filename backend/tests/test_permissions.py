from app.domain.permissions import Permission, has_permission, merge_permissions


def test_merge_permissions_uses_bitwise_or() -> None:
    value = merge_permissions([Permission.READ_MESSAGES, Permission.SEND_MESSAGES])

    assert has_permission(value, Permission.READ_MESSAGES)
    assert has_permission(value, Permission.SEND_MESSAGES)
    assert not has_permission(value, Permission.MANAGE_MESSAGES)


def test_administrator_implies_every_permission() -> None:
    value = merge_permissions([Permission.ADMINISTRATOR])

    assert has_permission(value, Permission.MOVE_MEMBERS)

