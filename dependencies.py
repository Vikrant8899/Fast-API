"""
Custom dependencies demonstrating dependency injection patterns.
Dependencies can be used for authentication, authorization, validation, etc.
"""
from fastapi import Header, HTTPException, Depends, Query
from typing import Optional
from sqlalchemy.orm import Session
from database import get_db


async def get_api_key(x_api_key: Optional[str] = Header(None)):
    """
    Dependency that validates an API key from headers.
    This is a simple example - in production, use proper authentication.
    
    Usage in routes:
        @app.get("/secure", dependencies=[Depends(get_api_key)])
    """
    if x_api_key != "secret-key-123":
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing API key"
        )
    return x_api_key


async def get_current_user_id(user_id: Optional[str] = Header(None, alias="X-User-ID")):
    """
    Dependency that extracts user ID from headers.
    Demonstrates how to use dependencies for user context.
    """
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="User ID header required"
        )
    return user_id


class CommonQueryParams:
    """
    Dependency class for common query parameters.
    Classes can be used as dependencies too!
    
    This demonstrates reusable pagination logic.
    """
    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
        search: Optional[str] = Query(None, description="Search term")
    ):
        self.skip = skip
        self.limit = limit
        self.search = search


def get_db_with_logging(db: Session = Depends(get_db)):
    """
    Example of chaining dependencies.
    This depends on get_db and adds logging functionality.
    """
    print(f"📊 Database session created: {id(db)}")
    try:
        yield db
    finally:
        print(f"📊 Database session closed: {id(db)}")
