# Bakery Management System

A comprehensive bakery management system built with Django that helps manage inventory, sales, suppliers, and production.

## Features

- Point of Sale (POS) system
- Inventory management
- Supplier management
- Production tracking
- Financial reporting
- Recipe management
- Stock alerts
- Sales tracking
- Expense tracking

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/bakery_management.git
cd bakery_management
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file with the following variables:
```
DJANGO_SECRET_KEY=your-secret-key
DB_NAME=bakery_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## Usage

- Access the admin interface at `/admin/`
- Use the dashboard at `/dashboard/`
- Manage products at `/products/`
- Handle sales at `/pos/`
- Track inventory at `/stock-report/`
- Manage suppliers at `/suppliers/`

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 