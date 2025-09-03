from fastapi import FastAPI
from database import engine, Base
from fastapi.middleware.cors import CORSMiddleware

# Import company modules
from companies import models as company_models
from companies.routes import router as company_router

# Import industry modules
from industries import models as industry_models
from industries.routes import router as industry_router

# Import group modules
from groups import models as group_models
from groups.routes import router as group_router

# Import division modules
from divisions import models as division_models
from divisions.routes import router as division_router

# Import person modules
from persons import models as person_models
from persons.routes import router as person_router

# Import audit log modules
from audit_logs import models as audit_log_models
from audit_logs.routes import router as audit_log_router

# Import email modules
from emails import models as email_models
from emails.routes import router as email_router

# Create all tables (both industries and companies will use the same Base)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Business Management API",
    description="API for managing industries and companies",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://data-management-nu.vercel.app" 
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include company routes
app.include_router(company_router, prefix="/companies", tags=["companies"])

# Include industry routes
app.include_router(industry_router, prefix="/industries", tags=["industries"])

# Include group routes
app.include_router(group_router, prefix="/groups", tags=["groups"])

# Include division routes
app.include_router(division_router, prefix="/divisions", tags=["divisions"])

# Include person routes
app.include_router(person_router, prefix="/persons", tags=["persons"])

# Include audit log routes
app.include_router(audit_log_router)

# Include email routes
app.include_router(email_router, prefix="/emails", tags=["emails"])

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Business Management API is running"}

@app.get("/")
def read_root():
    return {"message": "Business Management API is running"}

@app.get("/routes")
def get_routes():
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods)
            })
    return {"routes": routes}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)