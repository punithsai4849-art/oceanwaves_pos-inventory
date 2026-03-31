from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0004_employee_payslip_expense_pdf'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='barcode',
            field=models.CharField(
                blank=True, max_length=100,
                help_text='Barcode number'
            ),
        ),
    ]
