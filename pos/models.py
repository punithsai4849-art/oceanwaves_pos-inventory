from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import decimal, random, string
import uuid
from pathlib import Path
from datetime import timedelta

def _otp_default():
    return ''.join(random.choices(string.digits, k=6))


# ─────────────────────────────────────────────────────────────────────────────
#  STORE
# ─────────────────────────────────────────────────────────────────────────────
class Store(models.Model):
    name             = models.CharField(max_length=200)
    address          = models.TextField(blank=True)
    phone            = models.CharField(max_length=20, blank=True)
    whatsapp_number  = models.CharField(max_length=20, blank=True, help_text='Store WhatsApp number for sending bills (e.g. 919876543210)')
    email            = models.EmailField(blank=True)
    gstin            = models.CharField(max_length=20, blank=True, verbose_name="GSTIN")
    is_active        = models.BooleanField(default=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


# ─────────────────────────────────────────────────────────────────────────────
#  USER PROFILE  (ties a user to one store + role)
# ─────────────────────────────────────────────────────────────────────────────
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('SUPERADMIN', 'Super Admin'),   # sees everything across all stores
        ('SUBADMIN',   'Sub-Admin'),     # restricted admin permissions
        ('OWNER',      'Store Owner'),   # full access within assigned store
        ('STAFF',      'Staff'),         # billing + inventory in assigned store
        ('AREAMANAGER','Area Manager'),   # approves wholesale bills via OTP
        ('WHOLESALE_EXEC', 'Wholesale Executive'), # manage 4-5 stores, stock + wholesale approval
    ]
    user      = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role      = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STAFF')
    store     = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='staff')
    phone          = models.CharField(max_length=20, blank=True, help_text='Contact phone number')
    approval_pin   = models.CharField(max_length=128, blank=True, help_text='Hashed 4-6 digit approval PIN for wholesale approvals')
    is_active = models.BooleanField(default=True)
    
    # New fields
    permissions = models.JSONField(default=dict, blank=True, help_text='Restricted permissions for SUBADMIN')
    expires_at  = models.DateTimeField(null=True, blank=True, help_text='For temporary roles, access expires after this date')

    def __str__(self):
        return f"{self.user.username} ({self.role}) - {self.store}"

    @property
    def is_superadmin(self):
        return self.role == 'SUPERADMIN'

    @property
    def is_owner(self):
        return self.role in ('SUPERADMIN', 'OWNER')

    @property
    def is_staff_role(self):
        return self.role == 'STAFF'

    @property
    def is_area_manager(self):
        return self.role in ('AREAMANAGER', 'WHOLESALE_EXEC')

    @property
    def is_wholesale_exec(self):
        return self.role == 'WHOLESALE_EXEC'
        
    @property
    def is_subadmin(self):
        return self.role == 'SUBADMIN'
        
    @property
    def has_expired(self):
        if self.expires_at and timezone.now() > self.expires_at:
            return True
        return False


# ─────────────────────────────────────────────────────────────────────────────
#  PRODUCT  (scoped to a store)
# ─────────────────────────────────────────────────────────────────────────────
class Product(models.Model):
    CATEGORY_CHOICES = [
        ('FISH',   'Fish'),
        ('PRAWNS', 'Prawns'),
        ('CRAB',   'Crab'),
        ('OTHER',  'Other'),
    ]
    store            = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
    name             = models.CharField(max_length=200)
    barcode          = models.CharField(max_length=100, blank=True, help_text='Barcode number')
    category         = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='FISH')

    # Separate pricing for retail vs wholesale
    retail_price     = models.DecimalField(max_digits=10, decimal_places=2,
                                           help_text="Selling price for RETAIL (per kg)")
    wholesale_price  = models.DecimalField(max_digits=10, decimal_places=2,
                                           help_text="Selling price for WHOLESALE (per kg)")
    cost_price       = models.DecimalField(max_digits=10, decimal_places=2,
                                           help_text="Purchase / cost price (per kg)")

    stock_quantity   = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    low_stock_alert  = models.DecimalField(max_digits=10, decimal_places=3, default=5,
                                           help_text="Alert threshold in kg")
    is_active        = models.BooleanField(default=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.store.name}] {self.name}"

    @property
    def is_low_stock(self):
        return 0 < self.stock_quantity <= self.low_stock_alert

    @property
    def is_out_of_stock(self):
        return self.stock_quantity <= 0

    class Meta:
        ordering = ['category', 'name']


# ─────────────────────────────────────────────────────────────────────────────
#  SALE
# ─────────────────────────────────────────────────────────────────────────────
class Sale(models.Model):
    BILL_TYPE_CHOICES = [
        ('RETAIL',     'Retail'),
        ('WHOLESALE',  'Wholesale'),
    ]
    PAYMENT_MODE_CHOICES = [
        ('CASH',   'Cash'),
        ('UPI',    'UPI'),
        ('ONLINE', 'Online'),
        ('CARD',   'Card'),
        ('CREDIT', 'Credit'),
    ]

    store          = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='sales')
    bill_number    = models.CharField(max_length=60, unique=True)
    bill_type      = models.CharField(max_length=20, choices=BILL_TYPE_CHOICES, default='RETAIL')

    # Customer (required for wholesale)
    wholesale_customer = models.ForeignKey('WholesaleCustomer', on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    customer_name  = models.CharField(max_length=200, blank=True)
    customer_phone = models.CharField(max_length=15,  blank=True)
    customer_gst   = models.CharField(max_length=20,  blank=True)

    # Financials
    subtotal       = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gst_rate       = models.DecimalField(max_digits=5,  decimal_places=2, default=0)
    cgst_amount    = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sgst_amount    = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_gst      = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total    = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount       = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    payment_mode   = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES, default='CASH')
    notes          = models.TextField(blank=True)
    created_by     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at     = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"#{self.bill_number} [{self.store.name}] ₹{self.grand_total}"

    def save(self, *args, **kwargs):
        if not self.bill_number:
            # Store-scoped sequential bill numbers
            last = Sale.objects.filter(store=self.store).order_by('-id').first()
            num  = (last.id + 1) if last else 1
            pfx  = 'WS' if self.bill_type == 'WHOLESALE' else 'RT'
            # Use store id prefix to keep cross-store unique
            self.bill_number = f"S{self.store_id}-{pfx}{str(num).zfill(5)}"
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']


class SaleItem(models.Model):
    sale           = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product        = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_name   = models.CharField(max_length=200)   # snapshot
    quantity       = models.DecimalField(max_digits=10, decimal_places=3)
    cost_price     = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price  = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount   = models.DecimalField(max_digits=12, decimal_places=2)
    total_cost     = models.DecimalField(max_digits=12, decimal_places=2)
    profit         = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_amount = (self.quantity * self.selling_price).quantize(decimal.Decimal('0.01'))
        self.total_cost   = (self.quantity * self.cost_price).quantize(decimal.Decimal('0.01'))
        self.profit       = self.total_amount - self.total_cost
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} × {self.quantity} kg"


# ─────────────────────────────────────────────────────────────────────────────
#  STOCK LOG  (audit trail for every stock movement)
# ─────────────────────────────────────────────────────────────────────────────
class StockLog(models.Model):
    MOVEMENT_CHOICES = [
        ('IN',    'Stock In'),
        ('OUT',   'Sale'),
        ('ADJ',   'Adjustment'),
        ('WASTE', 'Waste / Damage'),
    ]
    store       = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='stock_logs')
    product     = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_logs')
    movement    = models.CharField(max_length=10, choices=MOVEMENT_CHOICES)
    quantity    = models.DecimalField(max_digits=10, decimal_places=3)
    balance     = models.DecimalField(max_digits=10, decimal_places=3)
    reference   = models.CharField(max_length=100, blank=True)   # bill number or note
    created_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at  = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} {self.movement} {self.quantity} kg"


# ─────────────────────────────────────────────────────────────────────────────
#  EXPENSE  (track store operational costs)
# ─────────────────────────────────────────────────────────────────────────────
class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('RENT',      'Rent'),
        ('SALARY',    'Salary'),
        ('UTILITIES', 'Utilities'),
        ('TRANSPORT', 'Transport'),
        ('PURCHASE',  'Stock Purchase'),
        ('OTHER',     'Other'),
    ]
    
    def expense_upload_path(instance, filename):
        ext = Path(filename).suffix.lower()
        return f"expense_bills/{uuid.uuid4().hex}{ext}"
        
    store       = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='expenses')
    category    = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.CharField(max_length=300)
    amount      = models.DecimalField(max_digits=12, decimal_places=2)
    bill_pdf    = models.FileField(upload_to=expense_upload_path, blank=True, null=True)
    date        = models.DateField(default=timezone.now)
    created_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"[{self.store.name}] {self.category} ₹{self.amount}"


# ─────────────────────────────────────────────────────────────────────────────
#  AREA MANAGER ↔ STORE  (ManyToMany, managed by admin)
# ─────────────────────────────────────────────────────────────────────────────
class AreaManagerStore(models.Model):
    """Links an Area Manager (UserProfile with role=AREAMANAGER) to one or many stores."""
    manager    = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE,
        related_name='managed_stores',
        limit_choices_to=models.Q(role='AREAMANAGER') | models.Q(role='WHOLESALE_EXEC')
    )
    store      = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='area_managers')
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='+')

    class Meta:
        unique_together = ('manager', 'store')
        ordering = ['store__name', 'manager__user__username']

    def __str__(self):
        return f"{self.manager.user.username} → {self.store.name}"


# ─────────────────────────────────────────────────────────────────────────────
#  WHOLESALE APPROVAL LOG  (audit trail of every wholesale approval)
# ─────────────────────────────────────────────────────────────────────────────
class WholesaleApproval(models.Model):
    """
    Records every wholesale bill approval.
    """
    store        = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='wholesale_approvals')
    area_manager = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE,
        related_name='approvals_given',
        limit_choices_to=models.Q(role='AREAMANAGER') | models.Q(role='WHOLESALE_EXEC')
    )
    sale         = models.OneToOneField('Sale', on_delete=models.CASCADE,
                                        related_name='approval', null=True, blank=True)
    bill_snapshot = models.JSONField(default=dict)   # snapshot at time of approval
    approved_by_name = models.CharField(max_length=200)  # denormalized for history
    created_by   = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='+')
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Approved by {self.approved_by_name} @ {self.store.name} on {self.created_at:%d/%m/%Y %H:%M}"


# ─────────────────────────────────────────────────────────────────────────────
#  EXPENSE v2  (with PDF bill upload + delete support)
# ─────────────────────────────────────────────────────────────────────────────
# We extend Expense by adding bill_pdf field via migration
# The Expense model above will get bill_pdf added in migration 0004

# ─────────────────────────────────────────────────────────────────────────────
#  EMPLOYEE
# ─────────────────────────────────────────────────────────────────────────────
class Employee(models.Model):
    EMPLOYMENT_TYPE = [
        ('FULLTIME',  'Full Time'),
        ('PARTTIME',  'Part Time'),
        ('CONTRACT',  'Contract'),
        ('DAILY',     'Daily Wage'),
    ]
    PAY_CYCLE = [
        ('MONTHLY',   'Monthly'),
        ('WEEKLY',    'Weekly'),
        ('DAILY',     'Daily'),
    ]

    store           = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='employees')
    user_profile    = models.OneToOneField(UserProfile, on_delete=models.SET_NULL,
                                           null=True, blank=True, related_name='employee')
    employee_id     = models.CharField(max_length=30, unique=True)
    full_name       = models.CharField(max_length=200)
    phone           = models.CharField(max_length=20, blank=True)
    email           = models.EmailField(blank=True)
    designation     = models.CharField(max_length=100, blank=True)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE, default='FULLTIME')
    pay_cycle       = models.CharField(max_length=20, choices=PAY_CYCLE, default='MONTHLY')
    basic_salary    = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    allowances      = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                          help_text='HRA, travel, food etc.')
    deductions      = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                          help_text='PF, ESI, tax etc.')
    date_joined     = models.DateField(default=timezone.now)
    is_active       = models.BooleanField(default=True)
    notes           = models.TextField(blank=True)
    created_by      = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='+')
    created_at      = models.DateTimeField(auto_now_add=True)

    @property
    def net_salary(self):
        return self.basic_salary + self.allowances - self.deductions

    def __str__(self):
        return f"{self.employee_id} — {self.full_name} ({self.store.name})"

    class Meta:
        ordering = ['store', 'full_name']


# ─────────────────────────────────────────────────────────────────────────────
#  PAY SLIP
# ─────────────────────────────────────────────────────────────────────────────
class PaySlip(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID',    'Paid'),
    ]
    MONTH_CHOICES = [
        (1,'January'),(2,'February'),(3,'March'),(4,'April'),
        (5,'May'),(6,'June'),(7,'July'),(8,'August'),
        (9,'September'),(10,'October'),(11,'November'),(12,'December'),
    ]

    employee        = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payslips')
    store           = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='payslips')
    month           = models.PositiveSmallIntegerField(choices=MONTH_CHOICES)
    year            = models.PositiveIntegerField()
    basic_salary    = models.DecimalField(max_digits=12, decimal_places=2)
    allowances      = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deductions      = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bonus           = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_pay         = models.DecimalField(max_digits=12, decimal_places=2)
    status          = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    payment_date    = models.DateField(null=True, blank=True)
    payment_mode    = models.CharField(max_length=30, blank=True)
    notes           = models.TextField(blank=True)
    created_by      = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='+')
    created_at      = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.net_pay = self.basic_salary + self.allowances + self.bonus - self.deductions
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.full_name} — {self.get_month_display()} {self.year} ₹{self.net_pay}"

    class Meta:
        ordering = ['-year', '-month']
        unique_together = ('employee', 'month', 'year')

# ─────────────────────────────────────────────────────────────────────────────
#  WHOLESALE CUSTOMERS & CREDIT TRACKING
# ─────────────────────────────────────────────────────────────────────────────
class WholesaleCustomer(models.Model):
    name                  = models.CharField(max_length=200, unique=True)
    phone                 = models.CharField(max_length=20, blank=True)
    email                 = models.EmailField(blank=True)
    gst                   = models.CharField(max_length=20, blank=True)
    is_credit_enabled     = models.BooleanField(default=True)
    credit_duration_days  = models.PositiveIntegerField(default=7, help_text="Minimum 7, Max 30 days")
    created_by            = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='+')
    created_at            = models.DateTimeField(auto_now_add=True)
    
    @property
    def has_unpaid_credit(self):
        return self.credit_records.filter(is_paid=False).exists()

    def __str__(self):
        return f"{self.name} - Credit: {'Yes' if self.is_credit_enabled else 'No'}"

class CreditRecord(models.Model):
    customer   = models.ForeignKey(WholesaleCustomer, on_delete=models.CASCADE, related_name='credit_records')
    sale       = models.OneToOneField(Sale, on_delete=models.CASCADE, related_name='credit_record', null=True, blank=True)
    
    amount     = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_external = models.BooleanField(default=False)
    external_reference = models.CharField(max_length=150, blank=True)
    
    due_date   = models.DateField()
    is_paid    = models.BooleanField(default=False)
    paid_on    = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_due(self):
        if self.is_external or not self.sale:
            return self.amount
        return self.sale.grand_total

    def __str__(self):
        ref = self.sale.bill_number if self.sale else self.external_reference
        return f"Credit for {self.customer.name} - #{ref} (Paid: {self.is_paid})"

