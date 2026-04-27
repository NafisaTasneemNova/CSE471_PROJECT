# Role-Based Authentication Usage Examples

This document demonstrates how to use the `require_buyer()` and `require_supplier()` dependency functions in FastAPI routes.

## Overview

The role-based authentication system provides two dependency functions:
- `require_buyer()`: Ensures the authenticated user has BUYER role
- `require_supplier()`: Ensures the authenticated user has SUPPLIER role

Both functions:
1. First validate the user is logged in (via `require_login()`)
2. Query the companies collection to get the user's company
3. Verify the company has the required role
4. Return HTTP 403 if role doesn't match

## Usage Examples

### Example 1: Buyer-Only Route

```python
@app.get("/api/dashboard/buyer/stats")
async def get_buyer_stats(user: dict = Depends(require_buyer)):
    """
    This endpoint is only accessible to users with BUYER role.
    The user parameter will contain the authenticated user's data.
    """
    from database import db
    
    # Calculate buyer-specific stats
    active_rfqs = await db["rfqs"].count_documents({
        "buyer_id": user.get("company_id"),
        "status": {"$in": ["OPEN", "EVALUATING"]}
    })
    
    return {
        "success": True,
        "stats": {
            "active_rfqs": active_rfqs
        }
    }
```

### Example 2: Supplier-Only Route

```python
@app.get("/api/dashboard/supplier/stats")
async def get_supplier_stats(user: dict = Depends(require_supplier)):
    """
    This endpoint is only accessible to users with SUPPLIER role.
    The user parameter will contain the authenticated user's data.
    """
    from database import db
    
    # Calculate supplier-specific stats
    active_bids = await db["bids"].count_documents({
        "supplier_id": user.get("company_id"),
        "status": {"$in": ["ACTIVE", "ACCEPTED"]}
    })
    
    return {
        "success": True,
        "stats": {
            "active_bids": active_bids
        }
    }
```

### Example 3: Buyer Dashboard Page

```python
@app.get("/dashboard/buyer", response_class=HTMLResponse)
async def buyer_dashboard(request: Request, user: dict = Depends(require_buyer)):
    """
    Render the buyer dashboard page.
    Only accessible to users with BUYER role.
    """
    from database import db
    
    # Fetch buyer's RFQs
    rfqs = await db["rfqs"].find({
        "buyer_id": user.get("company_id")
    }).to_list(length=10)
    
    return templates.TemplateResponse("buyer_dashboard.html", {
        "request": request,
        "user": user,
        "rfqs": rfqs
    })
```

### Example 4: Supplier Dashboard Page

```python
@app.get("/dashboard/supplier", response_class=HTMLResponse)
async def supplier_dashboard(request: Request, user: dict = Depends(require_supplier)):
    """
    Render the supplier dashboard page.
    Only accessible to users with SUPPLIER role.
    """
    from database import db
    
    # Fetch open RFQs for supplier
    rfqs = await db["rfqs"].find({
        "status": "OPEN"
    }).to_list(length=20)
    
    return templates.TemplateResponse("supplier_dashboard.html", {
        "request": request,
        "user": user,
        "rfqs": rfqs
    })
```

## Error Responses

### 401 Unauthorized
Returned when user is not logged in:
```json
{
    "detail": "Please log in to access this feature"
}
```

### 403 Forbidden - Wrong Role
Returned when user has wrong role (e.g., SUPPLIER trying to access buyer route):
```json
{
    "detail": "Buyer access required"
}
```

or

```json
{
    "detail": "Supplier access required"
}
```

### 403 Forbidden - Company Not Found
Returned when user's company doesn't exist:
```json
{
    "detail": "Company not found"
}
```

### 500 Internal Server Error
Returned when database is unavailable:
```json
{
    "detail": "Database not available"
}
```

## Testing

The implementation includes comprehensive unit tests in `test_role_auth.py`:

- ✅ `test_require_buyer_with_buyer_role` - Buyer can access buyer routes
- ✅ `test_require_buyer_with_supplier_role` - Supplier cannot access buyer routes
- ✅ `test_require_supplier_with_supplier_role` - Supplier can access supplier routes
- ✅ `test_require_supplier_with_buyer_role` - Buyer cannot access supplier routes
- ✅ `test_require_buyer_company_not_found` - Handles missing company
- ✅ `test_require_supplier_company_not_found` - Handles missing company
- ✅ `test_require_buyer_database_unavailable` - Handles database errors
- ✅ `test_require_supplier_database_unavailable` - Handles database errors

Run tests with:
```bash
python -m pytest test_role_auth.py -v
```

## Implementation Details

### Location
The functions are defined in `backend/main.py` in the "ACCESS CONTROL DEPENDENCY" section, right after the `require_login()` function.

### Dependencies
- `require_buyer()` and `require_supplier()` both depend on `require_login()`
- They use FastAPI's `Depends()` to chain dependencies
- They query the MongoDB `companies` collection to verify roles

### Database Query
Both functions perform a single database query:
```python
company = await db["companies"].find_one({"id": user.get("company_id")})
```

This query is efficient and uses the indexed `id` field.

## Best Practices

1. **Use the appropriate dependency** for each route based on the required role
2. **Don't bypass these dependencies** - they ensure data security
3. **Handle errors gracefully** in the frontend when receiving 403 responses
4. **Test role-based access** for all protected routes
5. **Consider caching** company role lookups if performance becomes an issue

## Related Requirements

This implementation satisfies the following requirements from the role-based-dashboards spec:

- **Requirement 1.3**: Role-based dashboard routing
- **Requirement 1.4**: Authorization error handling
- **Requirement 7.1**: Session validation
- **Requirement 7.3**: Data access filtering by company_id
