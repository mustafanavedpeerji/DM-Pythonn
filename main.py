from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas
from schemas import IndustryCreate
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pydantic import BaseModel

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class IndustryNameUpdate(BaseModel):
    industry_name: str

class IndustryParentUpdate(BaseModel):
    id: int
    new_parent_id: Optional[int] = None
    new_category: Optional[str] = None  # Added new category field

# Helper function to get category based on hierarchy level
def get_category_by_level(level: int) -> str:
    if level == 0:
        return "Main Industry"
    elif level == 1:
        return "sub"
    elif level == 2:
        return "sub-sub"
    elif level == 3:
        return "sub-sub-sub"
    else:
        # For deeper levels, continue the pattern
        category = "sub"
        for i in range(1, level):
            category += "-sub"
        return category

# Helper function to get the level of an industry in hierarchy
def get_industry_level(db: Session, industry_id: int) -> int:
    industry = db.query(models.Industry).filter(models.Industry.id == industry_id).first()
    if not industry or industry.parent_id is None:
        return 0
    return get_industry_level(db, industry.parent_id) + 1

# Helper function to update category of an industry and all its descendants
def update_industry_and_children_categories(db: Session, industry_id: int, new_level: int):
    industry = db.query(models.Industry).filter(models.Industry.id == industry_id).first()
    if industry:
        # Update current industry category
        industry.category = get_category_by_level(new_level)
        
        # Get all children and update their categories recursively
        children = db.query(models.Industry).filter(models.Industry.parent_id == industry_id).all()
        for child in children:
            update_industry_and_children_categories(db, child.id, new_level + 1)

# Check if parent_id is a descendant of child_id
def is_descendant(db: Session, child_id: int, parent_id: int, visited=None) -> bool:
    if visited is None:
        visited = set()
    
    if child_id == parent_id:
        return True
    
    if child_id in visited:
        return False
    
    visited.add(child_id)
    
    children = db.query(models.Industry).filter(models.Industry.parent_id == child_id).all()
    for child in children:
        if is_descendant(db, child.id, parent_id, visited):
            return True
    
    return False

@app.post("/industries/")
def create_industry(ind: schemas.IndustryCreate, db: Session = Depends(get_db)):
    try:
        # Create industry data
        industry_data = ind.dict()
        
        # Auto-assign category based on parent hierarchy level
        if industry_data.get('parent_id'):
            parent_level = get_industry_level(db, industry_data['parent_id'])
            industry_data['category'] = get_category_by_level(parent_level + 1)
        else:
            industry_data['category'] = "Main Industry"
        
        db_ind = models.Industry(**industry_data)
        db.add(db_ind)
        db.commit()
        db.refresh(db_ind)
        return db_ind
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating industry: {str(e)}")

@app.get("/industries/")
def get_industries(db: Session = Depends(get_db)):
    try:
        return db.query(models.Industry).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching industries: {str(e)}")

@app.post("/update-industry-parent")
def update_industry_parent(update: IndustryParentUpdate, db: Session = Depends(get_db)):
    try:
        industry = db.query(models.Industry).filter(models.Industry.id == update.id).first()
        if not industry:
            raise HTTPException(status_code=404, detail="Industry not found")

        # Validation checks
        if update.new_parent_id is not None:
            parent = db.query(models.Industry).filter(models.Industry.id == update.new_parent_id).first()
            if not parent:
                raise HTTPException(status_code=404, detail="Parent industry not found")
            if update.new_parent_id == update.id:
                raise HTTPException(status_code=400, detail="Industry cannot be its own parent")
            if is_descendant(db, update.id, update.new_parent_id):
                raise HTTPException(status_code=400, detail="Cannot move industry to its own descendant")

        # Update parent_id
        industry.parent_id = update.new_parent_id
        
        # Calculate new level and update categories
        if update.new_parent_id is None:
            # Moving to root level
            new_level = 0
        else:
            # Moving under a parent
            parent_level = get_industry_level(db, update.new_parent_id)
            new_level = parent_level + 1
        
        # Update the industry and all its children with correct categories
        update_industry_and_children_categories(db, update.id, new_level)
        
        db.commit()
        db.refresh(industry)
        return {"message": "Parent updated successfully", "industry": industry}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating parent: {str(e)}")

@app.put("/industries/{id}")
def update_industry(id: int, ind: IndustryNameUpdate, db: Session = Depends(get_db)):
    try:
        industry = db.query(models.Industry).filter(models.Industry.id == id).first()
        if not industry:
            raise HTTPException(status_code=404, detail="Industry not found")
        
        industry.industry_name = ind.industry_name
        db.commit()
        db.refresh(industry)
        return industry
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating industry: {str(e)}")

@app.delete("/industries/{id}")
def delete_industry(id: int, db: Session = Depends(get_db)):
    try:
        def get_all_children(parent_id, db):
            children = db.query(models.Industry).filter(models.Industry.parent_id == parent_id).all()
            all_children = list(children)
            for child in children:
                all_children.extend(get_all_children(child.id, db))
            return all_children
        
        industry = db.query(models.Industry).filter(models.Industry.id == id).first()
        if not industry:
            raise HTTPException(status_code=404, detail="Industry not found")
        
        children_to_delete = get_all_children(id, db)
        
        for child in children_to_delete:
            db.delete(child)
        
        db.delete(industry)
        db.commit()
        
        return {
            "message": f"Industry and {len(children_to_delete)} children deleted successfully",
            "deleted_count": len(children_to_delete) + 1
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting industry: {str(e)}")

@app.get("/industries/{id}")
def get_industry(id: int, db: Session = Depends(get_db)):
    try:
        industry = db.query(models.Industry).filter(models.Industry.id == id).first()
        if not industry:
            raise HTTPException(status_code=404, detail="Industry not found")
        return industry
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching industry: {str(e)}")

@app.get("/industries/{id}/children")
def get_industry_children(id: int, db: Session = Depends(get_db)):
    try:
        children = db.query(models.Industry).filter(models.Industry.parent_id == id).all()
        return children
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching children: {str(e)}")

# New endpoint to get industry hierarchy tree
@app.get("/industries/tree")
def get_industry_tree(db: Session = Depends(get_db)):
    try:
        all_industries = db.query(models.Industry).all()
        
        # Build tree structure
        industry_map = {ind.id: {
            "id": ind.id,
            "industry_name": ind.industry_name,
            "category": ind.category,
            "parent_id": ind.parent_id,
            "children": []
        } for ind in all_industries}
        
        tree = []
        for industry in all_industries:
            if industry.parent_id is None:
                tree.append(industry_map[industry.id])
            else:
                if industry.parent_id in industry_map:
                    industry_map[industry.parent_id]["children"].append(industry_map[industry.id])
        
        return tree
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error building tree: {str(e)}")

# New endpoint to fix existing categories (run once to update old data)
@app.post("/fix-categories")
def fix_existing_categories(db: Session = Depends(get_db)):
    try:
        # Get all root industries first
        root_industries = db.query(models.Industry).filter(models.Industry.parent_id == None).all()
        
        for root in root_industries:
            update_industry_and_children_categories(db, root.id, 0)
        
        db.commit()
        return {"message": "Categories fixed successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error fixing categories: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Industry API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)