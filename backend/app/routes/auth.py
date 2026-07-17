import jwt
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException

from app.schemas import RegisterRequest, LoginRequest
from app.main import supabase, get_password_hash, verify_password, JWT_SECRET, JWT_ALGORITHM, logger

router = APIRouter()


@router.post("/api/v1/auth/register")
async def register_user(request: RegisterRequest):
    """
    Register a new user and insert into Supabase with hashed password.
    """
    try:
        if not supabase:
            # For prototype if supabase is down, just return success
            return {"message": "User registered (Mock Mode)", "user": {"name": request.name, "email": request.email}}

        # 1. Check if email exists
        existing = supabase.table("tamweel_results").select("id").eq("email", request.email).execute()
        if existing.data:
            raise HTTPException(status_code=400, detail="Email already registered")

        # 2. Hash password
        hashed_password = get_password_hash(request.password)

        # 3. Insert new record
        new_user = {
            "name": request.name,
            "email": request.email,
            "password": hashed_password,
            "profession": "New User",
            "profession_category": "pending",
            "avg_monthly_income_jod": 0,
            "credit_score": 0,
            "risk_level": "Pending",
            "decision": "Pending",
            "approved_amount_jod": 0,
            "generated_at": datetime.now().isoformat()
        }

        response = supabase.table("tamweel_results").insert(new_user).execute()
        return {"message": "User registered successfully", "user": {"name": request.name, "email": request.email}}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Registration Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error during registration")


@router.post("/api/v1/auth/login")
async def login_user(request: LoginRequest):
    """
    Login user by verifying credentials against Supabase.
    """
    try:
        logger.info(f"Login attempt for email={request.email}")
        if not supabase:
            raise HTTPException(status_code=503, detail="Database unavailable. Cannot authenticate.")

        # Fetch user by email only
        response = supabase.table("tamweel_results").select("*").eq("email", request.email).execute()

        if not response.data:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user_record = response.data[0]
        stored_password = user_record.get('password')

        # Check password
        # Support both plaintext (from initial seed) and hashed passwords for prototype transitioning
        is_valid = False
        try:
            is_valid = verify_password(request.password, stored_password)
        except ValueError:
            # Fallback for old plaintext passwords from the seed script
            if request.password == stored_password:
                is_valid = True

        if not is_valid:
            logger.error(f"Login failed: is_valid=False for {request.email}. Stored hash matches? {stored_password is not None}")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Role is read exclusively from the `role` column in tamweel_results.
        # No email-substring heuristic. If the column is NULL or missing the row,
        # we default to 'user' — never elevate to 'sponsor' based on email content.
        # To grant a user sponsor access: UPDATE tamweel_results SET role='sponsor' WHERE email='...';
        db_role = user_record.get("role")

        if db_role not in ("user", "sponsor", "admin"):
            # Column missing or unexpected value — safe default is lowest privilege
            logger.warning(
                f"User {request.email} has unexpected role value '{db_role}' in DB. "
                "Defaulting to 'user'. Run add_role_column.sql migration if the column does not exist."
            )
            db_role = "user"
        role = db_role

        # Generate JWT
        token_payload = {
            "sub": request.email,
            "email": request.email,
            "role": role,
            "exp": datetime.now(timezone.utc) + timedelta(days=7)
        }
        access_token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

        return {
            "user": {
                "id": str(user_record.get('id', 'mock')),
                "name": user_record.get('name', 'Mock Name'),
                "email": request.email
            },
            "role": role,
            "access_token": access_token
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Login Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error during login")
