from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "account" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "email" VARCHAR(254)  UNIQUE,
    "google_id" TEXT,
    "created_at" INT NOT NULL,
    "updated_at" INT NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
