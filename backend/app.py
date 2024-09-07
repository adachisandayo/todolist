from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi import HTTPException
from sqlalchemy import ForeignKey, Table
from sqlalchemy.orm import relationship, joinedload

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 必要に応じて変更
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SQLite データベース設定
DATABASE_URL = "sqlite:///./my_database.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# モデル定義
# 中間テーブル
item_category = Table(
    "item_category",
    Base.metadata,
    Column("item_id", Integer, ForeignKey("item.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("category.id"), primary_key=True)
)

# Itemモデル
class Item(Base):
    __tablename__ = "item"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(80), nullable=False)

    categories = relationship("Category", secondary=item_category, back_populates="items")

# Categoryモデル
class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(80), nullable=False)

    items = relationship("Item", secondary=item_category, back_populates="categories")


# データベース初期化
Base.metadata.create_all(bind=engine)

# Pydanticモデル (POSTのためのリクエストボディのスキーマ)
class ItemCreate(BaseModel):
    name: str

class CategoryCreate(BaseModel):
    name: str

class ItemCategoryCreate(BaseModel):
    item_id: int
    category_id: int


@app.get("/")
async def read_root():
    return {"message": "Hello from FastAPI!"}

@app.get("/items")
async def get_items():
    # データベースセッションの作成
    session: Session = SessionLocal()
    items = session.query(Item).options(joinedload(Item.categories)).all()
    session.close()
    item_dict = []
    for item in items:
        item_dict.append({
                        "id":item.id,
                        "name": item.name, 
                        "categories": [category.name for category in item.categories]
                        })
    print(item_dict)
    return item_dict

@app.post("/items", status_code=201)
async def add_item(item: ItemCreate):
    # データベースセッションの作成
    session: Session = SessionLocal()
    new_item = Item(name=item.name)
    session.add(new_item)
    session.commit()
    session.close()
    return {"message": "Item added successfully."}

# DELETEリクエストのエンドポイント
@app.delete("/items/{id}", status_code=200)
async def delete_item(id: int):
    session: Session = SessionLocal()
    item = session.query(Item).get(id)
    if not item:
        session.close()
        raise HTTPException(status_code=404, detail="Item not found")
    
    session.delete(item)
    session.commit()
    session.close()
    return {"message": "Item deleted successfully."}

# PUTリクエストのエンドポイント
@app.put("/items/{id}", status_code=200)
async def update_item(id: int, item_update: ItemCreate):
    session: Session = SessionLocal()
    item = session.query(Item).get(id)
    if not item:
        session.close()
        raise HTTPException(status_code=404, detail="Item not found")
    
    # アイテムのデータを更新
    item.name = item_update.name
    session.commit()
    session.close()
    return {"message": "Item updated successfully."}

#タグのCRUD
@app.get("/categories")
async def get_categories():
    session: Session = SessionLocal()
    categories = session.query(Category).all()
    session.close()
    category_dict = {category.id: category.name for category in categories}
    # print(category_dict)
    return category_dict

@app.post("/categories", status_code=201)
async def add_category(category: CategoryCreate):
    session: Session = SessionLocal()
    new_category = Category(name=category.name)
    session.add(new_category)
    session.commit()
    session.close()
    return {"message": "Item added successfully."}

@app.delete("/categories/{id}", status_code=200)
async def delete_category(id: int):
    session: Session = SessionLocal()
    category = session.query(Category).get(id)
    if not category:
        session.close()
        raise HTTPException(status_code=404, detail="Category not found")
    
    session.delete(category)
    session.commit()
    session.close()
    return {"message": "Category deleted successfully."}


# 新しいItemCategoryインスタンスを追加するためのエンドポイント
@app.post("/itemcategory", status_code=200)
async def add_item_category(item_category_data: ItemCategoryCreate):
    session: Session = SessionLocal()
    
    # 新しいItemCategoryインスタンスを作成
    new_instance = item_category.insert().values(
        item_id=item_category_data.item_id, 
        category_id=item_category_data.category_id
    )
    
    # データベースに追加
    session.execute(new_instance)
    session.commit()
    session.close()
    
    return {"message": "ItemCategory added successfully."}