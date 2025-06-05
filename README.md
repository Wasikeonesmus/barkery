# Bakery Management System

A comprehensive bakery management system built with Django that helps manage sales, inventory, suppliers, and financial reporting.

## Features

- Point of Sale (POS) system
- Inventory management
- Supplier management
- Production batch tracking
- Financial reporting
- User authentication and authorization

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Wasikeonesmus/barkery.git
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
DJANGO_SECRET_KEY=your_secret_key
DEBUG=True
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

1. Access the admin interface at `http://localhost:8000/admin`
2. Access the dashboard at `http://localhost:8000/dashboard`
3. Use the POS system at `http://localhost:8000/pos`

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.
