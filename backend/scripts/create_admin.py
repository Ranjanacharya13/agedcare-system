"""Create the first administrator account."""

import argparse
import asyncio
import getpass
import sys

from backend.db.supabase_client import close_supabase_connection, connect_to_supabase, get_supabase
from backend.models.user import AccessRole
from backend.repositories.user_repository import UserRepository
from backend.schemas.user import MIN_PASSWORD_LENGTH, UserCreate
from backend.services.auth_service import AuthService
from backend.services.login_throttle import LoginThrottle


def _prompt_password() -> str:
    while True:
        password = getpass.getpass("Password: ")
        if len(password) < MIN_PASSWORD_LENGTH:
            print(f"  Too short — at least {MIN_PASSWORD_LENGTH} characters.", file=sys.stderr)
            continue
        if password != getpass.getpass("Confirm password: "):
            print("  Passwords did not match.", file=sys.stderr)
            continue
        return password


async def main() -> int:
    parser = argparse.ArgumentParser(description="Create a user account.")
    parser.add_argument("--email")
    parser.add_argument("--full-name", default=None)
    parser.add_argument(
        "--role",
        default=AccessRole.ADMIN.value,
        choices=[r.value for r in AccessRole],
    )
    args = parser.parse_args()

    email = args.email or input("Email: ")
    password = _prompt_password()

    await connect_to_supabase()
    try:
        service = AuthService(UserRepository(get_supabase()), LoginThrottle())
        user = await service.create_user(
            UserCreate(
                email=email,
                password=password,
                access_role=AccessRole(args.role),
                full_name=args.full_name,
            )
        )
    finally:
        await close_supabase_connection()

    print(f"Created {user.access_role.value}: {user.email} ({user.id})")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
