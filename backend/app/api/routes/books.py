"""Book management routes."""
import uuid
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import CurrentUser
from app.core.database import get_db
from app.models.book import Book
from app.models.borrow import BorrowRecord
from app.schemas.book import Book as BookSchema
from app.schemas.book import BookList, BookUpdate
from app.services.recommendations import RecommendationEngine
from app.services.storage import get_storage_provider
from app.services.tasks import schedule_book_summarization

router = APIRouter(prefix="/books", tags=["Books"])


@router.post("", response_model=BookSchema, status_code=status.HTTP_201_CREATED)
async def create_book(
    title: Annotated[str, Form()],
    author: Annotated[str, Form()],
    file: Annotated[UploadFile, File()],
    isbn: Annotated[str | None, Form()] = None,
    description: Annotated[str | None, Form()] = None,
    published_year: Annotated[int | None, Form()] = None,
    genre: Annotated[str | None, Form()] = None,
    total_copies: Annotated[int, Form()] = 1,
    current_user: CurrentUser = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> Book:
    """
    Upload a new book with file content.
    
    This triggers async summarization of the book content.
    """
    # Validate file type
    allowed_types = ["text/plain", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not supported. Allowed: {allowed_types}",
        )
    
    # Determine file extension
    file_ext = "txt" if file.content_type == "text/plain" else "pdf"
    
    # Generate unique file path
    file_name = f"{uuid.uuid4()}.{file_ext}"
    file_path = f"books/{file_name}"
    
    # Get file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    # Upload to storage
    storage = get_storage_provider()
    await storage.upload_file(file.file, file_path, file.content_type)
    
    # Create book record
    book = Book(
        title=title,
        author=author,
        isbn=isbn,
        description=description,
        published_year=published_year,
        genre=genre,
        file_path=file_path,
        file_type=file_ext,
        file_size=file_size,
        total_copies=total_copies,
        available_copies=total_copies,
    )
    
    db.add(book)
    await db.commit()
    await db.refresh(book)
    
    # Schedule async summarization
    schedule_book_summarization(book.id)
    
    return book


@router.get("", response_model=BookList)
async def list_books(
    page: int = 1,
    page_size: int = 20,
    genre: str | None = None,
    author: str | None = None,
    search: str | None = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> BookList:
    """
    List books with pagination and filtering.
    """
    # Build query
    query = select(Book)
    
    if genre:
        query = query.where(Book.genre == genre)
    if author:
        query = query.where(Book.author.ilike(f"%{author}%"))
    if search:
        query = query.where(
            (Book.title.ilike(f"%{search}%")) | (Book.author.ilike(f"%{search}%"))
        )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # Execute query
    result = await db.execute(query)
    books = result.scalars().all()
    
    pages = (total + page_size - 1) // page_size
    
    return BookList(
        items=books,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/{book_id}", response_model=BookSchema)
async def get_book(
    book_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Book:
    """Get book details by ID."""
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    return book


@router.put("/{book_id}", response_model=BookSchema)
async def update_book(
    book_id: int,
    book_data: BookUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Book:
    """Update book metadata."""
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    # Update fields
    update_data = book_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(book, field, value)

    # Adjust available copies if total copies changed
    if "total_copies" in update_data:
        diff = update_data["total_copies"] - book.total_copies
        book.available_copies = max(0, book.available_copies + diff)

    await db.commit()
    await db.refresh(book)

    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a book and its associated file."""
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    # Delete file from storage
    storage = get_storage_provider()
    await storage.delete_file(book.file_path)

    # Delete book record
    await db.delete(book)
    await db.commit()


@router.post("/{book_id}/borrow", status_code=status.HTTP_201_CREATED)
async def borrow_book(
    book_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Borrow a book."""
    # Get book
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    # Check availability
    if book.available_copies <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No copies available",
        )

    # Check if user already has an active borrow
    active_borrow = await db.execute(
        select(BorrowRecord)
        .where(BorrowRecord.user_id == current_user.id)
        .where(BorrowRecord.book_id == book_id)
        .where(BorrowRecord.returned_at.is_(None))
    )
    if active_borrow.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have this book borrowed",
        )

    # Create borrow record
    due_date = datetime.utcnow() + timedelta(days=14)  # 2 weeks
    borrow = BorrowRecord(
        user_id=current_user.id,
        book_id=book_id,
        due_date=due_date,
    )
    db.add(borrow)

    # Update available copies
    book.available_copies -= 1

    await db.commit()

    # Update user preferences
    engine = RecommendationEngine(db)
    await engine.update_user_preferences(current_user.id)

    return {"message": "Book borrowed successfully", "due_date": due_date}


@router.post("/{book_id}/return", status_code=status.HTTP_200_OK)
async def return_book(
    book_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Return a borrowed book."""
    # Find active borrow record
    result = await db.execute(
        select(BorrowRecord)
        .where(BorrowRecord.user_id == current_user.id)
        .where(BorrowRecord.book_id == book_id)
        .where(BorrowRecord.returned_at.is_(None))
    )
    borrow = result.scalar_one_or_none()

    if not borrow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active borrow record found",
        )

    # Mark as returned
    borrow.returned_at = datetime.utcnow()

    # Update available copies
    book_result = await db.execute(select(Book).where(Book.id == book_id))
    book = book_result.scalar_one()
    book.available_copies += 1

    await db.commit()

    return {"message": "Book returned successfully"}

