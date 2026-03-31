from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0003_pin_approval'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        # Add bill_pdf to existing Expense model
        migrations.AddField(
            model_name='expense',
            name='bill_pdf',
            field=models.FileField(
                blank=True, null=True,
                upload_to='expense_bills/',
                help_text='Upload bill/invoice PDF'
            ),
        ),

        # Employee model
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('employee_id',     models.CharField(max_length=30, unique=True)),
                ('full_name',       models.CharField(max_length=200)),
                ('phone',           models.CharField(blank=True, max_length=20)),
                ('email',           models.EmailField(blank=True)),
                ('designation',     models.CharField(blank=True, max_length=100)),
                ('employment_type', models.CharField(
                    choices=[('FULLTIME','Full Time'),('PARTTIME','Part Time'),
                             ('CONTRACT','Contract'),('DAILY','Daily Wage')],
                    default='FULLTIME', max_length=20)),
                ('pay_cycle', models.CharField(
                    choices=[('MONTHLY','Monthly'),('WEEKLY','Weekly'),('DAILY','Daily')],
                    default='MONTHLY', max_length=20)),
                ('basic_salary', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('allowances',   models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('deductions',   models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('date_joined',  models.DateField(default=django.utils.timezone.now)),
                ('is_active',    models.BooleanField(default=True)),
                ('notes',        models.TextField(blank=True)),
                ('created_at',   models.DateTimeField(auto_now_add=True)),
                ('store', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='employees', to='pos.store')),
                ('user_profile', models.OneToOneField(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='employee', to='pos.userprofile')),
                ('created_by', models.ForeignKey(
                    null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='+', to='auth.user')),
            ],
            options={'ordering': ['store', 'full_name']},
        ),

        # PaySlip model
        migrations.CreateModel(
            name='PaySlip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('month', models.PositiveSmallIntegerField(choices=[
                    (1,'January'),(2,'February'),(3,'March'),(4,'April'),
                    (5,'May'),(6,'June'),(7,'July'),(8,'August'),
                    (9,'September'),(10,'October'),(11,'November'),(12,'December'),
                ])),
                ('year',         models.PositiveIntegerField()),
                ('basic_salary', models.DecimalField(decimal_places=2, max_digits=12)),
                ('allowances',   models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('deductions',   models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('bonus',        models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('net_pay',      models.DecimalField(decimal_places=2, max_digits=12)),
                ('status', models.CharField(
                    choices=[('PENDING','Pending'),('PAID','Paid')],
                    default='PENDING', max_length=10)),
                ('payment_date', models.DateField(blank=True, null=True)),
                ('payment_mode', models.CharField(blank=True, max_length=30)),
                ('notes',        models.TextField(blank=True)),
                ('created_at',   models.DateTimeField(auto_now_add=True)),
                ('employee', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='payslips', to='pos.employee')),
                ('store', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='payslips', to='pos.store')),
                ('created_by', models.ForeignKey(
                    null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='+', to='auth.user')),
            ],
            options={'ordering': ['-year', '-month'],
                     'unique_together': {('employee', 'month', 'year')}},
        ),
    ]
