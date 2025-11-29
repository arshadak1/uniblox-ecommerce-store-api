# File Structure
```commandline
uniblox-ecommerce-store-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py              # Configuration settings
│   ├── models/
│   │   ├── __init__.py
│   │   └── schema.py         # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── cart_service.py    # Cart business logic
│   │   ├── checkout_service.py # Checkout & discount logic
│   │   └── admin_service.py   # Admin operations
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── repository.py # In-memory data store
│   └── routers/
│       ├── __init__.py
│       ├── cart.py            # Cart endpoints
│       ├── checkout.py        # Checkout endpoints
│       └── admin.py           # Admin endpoints
├── tests/
│   ├── __init__.py
│   ├── test_cart.py
│   └── test_checkout.py
├── requirements.txt
├── README.md
└── .gitignore
```

# Project Setup
Prerequisites

- Python 3.13 or higher
- pip (Python package manager)

```bash
# Clone the repository
git clone <your-repo-url>
cd ecommerce-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app.main:app --reload

# Run tests
pytest
```

# API Endpoints
## Cart Management:

- `POST /api/v1/cart/add` - Add item to cart
- `PUT /api/v1/cart/update` - Update item quantity
- `DELETE /api/v1/cart/remove/{product_id}` - Remove item
- `GET /api/v1/cart` - View cart

## Checkout:

- `POST /api/v1/checkout` - Process order

## Admin
- `POST /api/v1/admin/generate-discount` - Generate discount code
- `GET /api/v1/admin/stats` - View statistics
- `GET /api/v1/admin/users` - Get Users List

# Docs URL
- `/docs`