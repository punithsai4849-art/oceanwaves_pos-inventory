# 🌊 Ocean Waves Sea Foods — Multi-Store POS v2

A full-featured multi-store Point of Sale system built with Django + MySQL.

---

## 🏪 Multi-Store Architecture

```
Super Admin
├── Store 1 (e.g. Banjara Hills)
│   ├── Owner A  → full access to Store 1 only
│   └── Staff B  → billing + inventory for Store 1 only
└── Store 2 (e.g. Jubilee Hills)
    └── Staff C  → billing + inventory for Store 2 only
```

- Users **cannot** access another store's data
- Super Admin sees **all stores** from a global dashboard
- Each store has **separate inventory, billing, and reports**

---

## ⚡ Quick Start

### 1. Create MySQL Database
```sql
CREATE DATABASE oceanwaves_pos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Configure Database
Edit `oceanwaves_project/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'oceanwaves_pos',
        'USER': 'root',
        'PASSWORD': 'your_password',   # ← CHANGE THIS
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 3. Install & Migrate
```bash
pip install -r requirements.txt
python manage.py migrate
```

### 4. Create Super Admin
```bash
python manage.py createsuperuser
```
Then create their UserProfile in Django shell:
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import User
from pos.models import UserProfile

user = User.objects.get(username='your_superadmin_username')
UserProfile.objects.create(user=user, role='SUPERADMIN', store=None)
print("Super Admin profile created!")
exit()
```

### 5. Run
```bash
python manage.py runserver
```
Open: **http://localhost:8000**

---

## 🏗️ How to Set Up Stores & Users (via UI)

1. **Login** as Super Admin
2. Go to **Stores** → Create stores (name, address, phone, GSTIN)
3. Go to **Users** → Create users, assign role and store
4. Staff/Owner login → they only see their store

---

## 👥 Role Permissions

| Feature | Super Admin | Store Owner | Staff |
|---------|:-----------:|:-----------:|:-----:|
| Global dashboard | ✅ | ❌ | ❌ |
| Create / manage stores | ✅ | ❌ | ❌ |
| Create / assign users | ✅ | ❌ | ❌ |
| Billing (own store) | ❌ | ✅ | ✅ |
| Inventory (own store) | ❌ | ✅ | ✅ |
| Restock products | ❌ | ✅ | ✅ |
| Delete products | ❌ | ✅ | ❌ |
| Reports + Export | ✅ | ✅ | ❌ |
| Record expenses | ❌ | ✅ | ❌ |
| Stock log | ❌ | ✅ | ✅ |
| View cost price | ✅ | ✅ (inventory) | ❌ |

---

## 💰 Dual Pricing System

Each product has **3 prices**:
- **Cost Price (C.P)** — purchase price (hidden on billing screen)
- **Retail Price** — used when bill type = RETAIL
- **Wholesale Price** — used when bill type = WHOLESALE

When you switch bill type on the POS screen, **cart prices auto-update** instantly.

---

## 🧾 Bill Types

### Retail
- Uses retail price for all items
- No GST
- Simple receipt (thermal)
- No customer details required

### Wholesale (GST Invoice)
- Uses wholesale price for all items
- Choose GST: 5% / 12% / 18% / 28%
- Auto-calculates CGST + SGST
- Requires customer name
- Generates A4 Tax Invoice + thermal receipt
- Customer GSTIN field available

---

## 🖨️ Print Formats
- **Thermal 80mm** — for all bills (auto-prints on save)
- **A4 Tax Invoice** — wholesale bills only, includes GSTIN, GST breakdown

---

## 📊 Additional Features

- **Expense Tracking** — record rent, salary, utilities per store per day
- **Net Profit** = Gross Profit − Expenses
- **Stock Log** — complete audit trail: every stock IN/OUT logged
- **Low Stock Alerts** — configurable per product
- **Discount** — apply ₹ discount on any bill
- **Payment modes** — Cash, UPI, Online, Card
- **Excel Export** — multi-store or single-store by date

---

## 📁 Project Structure

```
oceanwaves_v2/
├── manage.py
├── requirements.txt
├── oceanwaves_project/
│   ├── settings.py       ← DB config here
│   └── urls.py
└── pos/
    ├── models.py         ← Store, UserProfile, Product, Sale, SaleItem, StockLog, Expense
    ├── views.py          ← All business logic
    ├── urls.py
    ├── admin.py
    ├── migrations/
    ├── templates/pos/
    │   ├── base.html
    │   ├── login.html
    │   ├── dashboard_admin.html   ← Super Admin cross-store view
    │   ├── dashboard_store.html   ← Per-store dashboard
    │   ├── stores.html            ← Store management
    │   ├── store_detail.html      ← Store report (admin)
    │   ├── users.html             ← User management
    │   ├── billing.html           ← POS screen
    │   ├── inventory.html         ← Inventory
    │   ├── reports.html           ← Sales reports
    │   ├── stock_log.html         ← Stock audit log
    │   ├── bill_print.html        ← Thermal + A4 print
    │   └── no_store.html
    └── static/pos/
        ├── css/style.css, billing.css
        ├── js/main.js, billing.js
        └── images/logo.jpg
```

---

## 🔧 SQLite (Quick Test)

Comment out MySQL and uncomment in `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```
# oceanwaves_pos-inventory
