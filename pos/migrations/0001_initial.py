from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        # Store
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('address', models.TextField(blank=True)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('email', models.EmailField(blank=True)),
                ('gstin', models.CharField(blank=True, max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['name']},
        ),
        # UserProfile
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('role', models.CharField(choices=[('SUPERADMIN','Super Admin'),('OWNER','Store Owner'),('STAFF','Staff')], default='STAFF', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('store', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='staff', to='pos.store')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to='auth.user')),
            ],
        ),
        # Product
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('category', models.CharField(choices=[('FISH','Fish'),('PRAWNS','Prawns'),('CRAB','Crab'),('OTHER','Other')], default='FISH', max_length=20)),
                ('cost_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('retail_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('wholesale_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stock_quantity', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('low_stock_alert', models.DecimalField(decimal_places=3, default=5, max_digits=10)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='pos.store')),
            ],
            options={'ordering': ['category', 'name']},
        ),
        # Sale
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('bill_number', models.CharField(max_length=60, unique=True)),
                ('bill_type', models.CharField(choices=[('RETAIL','Retail'),('WHOLESALE','Wholesale')], default='RETAIL', max_length=20)),
                ('customer_name', models.CharField(blank=True, max_length=200)),
                ('customer_phone', models.CharField(blank=True, max_length=15)),
                ('customer_gst', models.CharField(blank=True, max_length=20)),
                ('subtotal', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('gst_rate', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('cgst_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('sgst_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('total_gst', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('grand_total', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('discount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('payment_mode', models.CharField(choices=[('CASH','Cash'),('UPI','UPI'),('ONLINE','Online'),('CARD','Card')], default='CASH', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales', to='pos.store')),
            ],
            options={'ordering': ['-created_at']},
        ),
        # SaleItem
        migrations.CreateModel(
            name='SaleItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('product_name', models.CharField(max_length=200)),
                ('quantity', models.DecimalField(decimal_places=3, max_digits=10)),
                ('cost_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('selling_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('total_cost', models.DecimalField(decimal_places=2, max_digits=12)),
                ('profit', models.DecimalField(decimal_places=2, max_digits=12)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='pos.product')),
                ('sale', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='pos.sale')),
            ],
        ),
        # StockLog
        migrations.CreateModel(
            name='StockLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('movement', models.CharField(choices=[('IN','Stock In'),('OUT','Sale'),('ADJ','Adjustment'),('WASTE','Waste / Damage')], max_length=10)),
                ('quantity', models.DecimalField(decimal_places=3, max_digits=10)),
                ('balance', models.DecimalField(decimal_places=3, max_digits=10)),
                ('reference', models.CharField(blank=True, max_length=100)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock_logs', to='pos.product')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock_logs', to='pos.store')),
            ],
            options={'ordering': ['-created_at']},
        ),
        # Expense
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('category', models.CharField(choices=[('RENT','Rent'),('SALARY','Salary'),('UTILITIES','Utilities'),('TRANSPORT','Transport'),('PURCHASE','Stock Purchase'),('OTHER','Other')], max_length=20)),
                ('description', models.CharField(max_length=300)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expenses', to='pos.store')),
            ],
            options={'ordering': ['-date', '-created_at']},
        ),
    ]
