from asyncpg import UniqueViolationError

from app.db.pool import database
from app.domain.snowflake import SnowflakeGenerator
from app.schemas.auth import UserPublic

id_generator = SnowflakeGenerator(worker_id=3)


class UserRepository:
    async def create_user(self, username: str, password_hash: str) -> UserPublic:
        user_id = id_generator.generate()
        try:
            row = await database.fetchrow(
                """
                INSERT INTO users (id, username, password_hash, status)
                VALUES ($1, $2, $3, 1)
                RETURNING id, username, status
                """,
                user_id,
                username,
                password_hash,
            )
        except UniqueViolationError as exc:
            raise ValueError("username already exists") from exc
        if row is None:
            raise RuntimeError("user insert did not return a row")
        return UserPublic(
            id=int(row["id"]),
            username=str(row["username"]),
            status=int(row["status"]),
        )

    async def get_by_username_with_password(self, username: str) -> tuple[UserPublic, str] | None:
        row = await database.fetchrow(
            """
            SELECT id, username, status, password_hash
            FROM users
            WHERE username = $1
            """,
            username,
        )
        if row is None:
            return None
        return (
            UserPublic(
                id=int(row["id"]),
                username=str(row["username"]),
                status=int(row["status"]),
            ),
            str(row["password_hash"]),
        )


user_repository = UserRepository()
