from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, joinedload
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB設定
DATABASE_URL = "sqlite+aiosqlite:///./my_database.db"  # 非同期対応のSQLite URL
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

Base = declarative_base()

item_category_table = Table(
    "item_category", Base.metadata,
    Column("item_id", Integer, ForeignKey("item.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("category.id"), primary_key=True)
)

class Item(Base):
    __tablename__ = "item"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    categories = relationship("Category", secondary=item_category_table, back_populates="items")

class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    items = relationship("Item", secondary=item_category_table, back_populates="categories")


# Pydanticモデル
class ItemCreate(BaseModel):
    name: str

class CategoryCreate(BaseModel):
    name: str

# DBセッションを取得する依存関係
async def get_db():
    async with SessionLocal() as session:
        yield session

# ルート
@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}

# 非同期処理を使用したGETリクエスト
@app.get("/items")
async def get_items(db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(Item).options(joinedload(Item.categories)))
        items = result.scalars().all()
        item_list = [
            {"id": item.id, "name": item.name, "categories": [category.name for category in item.categories]}
            for item in items
        ]
        return item_list

# 非同期処理を使用したPOSTリクエスト
@app.post("/items", status_code=201)
async def add_item(item: ItemCreate, db: AsyncSession = Depends(get_db)):
    new_item = Item(name=item.name)
    db.add(new_item)
    await db.commit()
    return {"message": "Item added successfully."}

# 同期/非同期対応の削除リクエスト
@app.delete("/items/{id}", status_code=200)
async def delete_item(id: int, db: AsyncSession = get_db()):
    async with db as session:
        item = await session.get(Item, id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        await session.delete(item)
        await session.commit()
        return {"message": "Item deleted successfully."}

# 更新処理
@app.put("/items/{id}", status_code=200)
async def update_item(id: int, item: ItemCreate, db: AsyncSession = get_db()):
    async with db as session:
        existing_item = await session.get(Item, id)
        if not existing_item:
            raise HTTPException(status_code=404, detail="Item not found")
        existing_item.name = item.name
        await session.commit()
        return {"message": "Item updated successfully."}

# カテゴリ関連のルート
@app.get("/categories")
async def get_categories(db: AsyncSession = get_db()):
    async with db as session:
        result = await session.execute(select(Category))
        categories = result.scalars().all()
        category_dict = {category.id: category.name for category in categories}
        return category_dict

@app.post("/categories", status_code=201)
async def add_category(category: CategoryCreate, db: AsyncSession = get_db()):
    new_category = Category(name=category.name)
    db.add(new_category)
    await db.commit()
    return {"message": "Category added successfully."}

# カテゴリ削除
@app.delete("/categories/{id}", status_code=200)
async def delete_category(id: int, db: AsyncSession = get_db()):
    async with db as session:
        category = await session.get(Category, id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        await session.delete(category)
        await session.commit()
        return {"message": "Category deleted successfully."}

# アイテムとカテゴリの関係追加
@app.post("/itemcategory", status_code=201)
async def add_itemcategory(item_id: int, category_id: int, db: AsyncSession = get_db()):
    new_instance = ItemCategory(item_id=item_id, category_id=category_id)
    db.add(new_instance)
    await db.commit()
    return {"message": "Tag added successfully."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
