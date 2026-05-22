from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr
from typing import List

# ----------------------------------------------------------------
# 1. 데이터베이스 및 SQLAlchemy 설정
# ----------------------------------------------------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# SQLite는 기본적으로 싱글 스레드에서만 동작하도록 제한되어 있어, 
# FastAPI의 멀티스레드 환경을 위해 check_same_thread를 False로 설정합니다.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ----------------------------------------------------------------
# 2. SQLAlchemy 모델 (DB 테이블 구조)
# ----------------------------------------------------------------
class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)


# 애플리케이션 시작 시 자동으로 테이블을 생성합니다.
Base.metadata.create_all(bind=engine)


# ----------------------------------------------------------------
# 3. Pydantic 모델 (요청 및 응답 스키마 검증)
# ----------------------------------------------------------------
class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    pass  # 생성할 때 받을 데이터

class UserUpdate(UserBase):
    pass  # 수정할 때 받을 데이터

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True  # SQLAlchemy 모델 데이터를 Pydantic으로 변환 허용


# ----------------------------------------------------------------
# 4. 의존성 주입 (DB 세션 관리)
# ----------------------------------------------------------------
def get_db():
    """요청이 들어올 때 DB 세션을 생성하고, 요청이 끝나면 닫아줍니다."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------------------------------------------
# 5. FastAPI 앱 및 CRUD API 엔드포인트 구현
# ----------------------------------------------------------------
app = FastAPI(title="FastAPI SQLite CRUD Example")


# [CREATE] 유저 생성
@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # 이메일 중복 체크
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")
    
    new_user = UserModel(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # DB에 생성된 ID를 받아옴
    return new_user


# [READ] 유저 목록 조회
@app.get("/users", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users


# [READ] 특정 유저 상세 조회
@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    return user


# [UPDATE] 유저 정보 수정
@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, updated_user: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    
    user.name = updated_user.name
    user.email = updated_user.email
    
    db.commit()
    db.refresh(user)
    return user


# [DELETE] 유저 삭제
@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    
    db.delete(user)
    db.commit()
    return None  # 204 No Content는 본문을 반환하지 않습니다.