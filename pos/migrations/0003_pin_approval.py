from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0002_area_manager_otp'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        # Add approval_pin field to UserProfile
        migrations.AddField(
            model_name='userprofile',
            name='approval_pin',
            field=models.CharField(
                blank=True, max_length=128,
                help_text='Hashed 4-6 digit approval PIN for wholesale approvals'
            ),
        ),

        # Drop WholesaleOTP table
        migrations.DeleteModel(name='WholesaleOTP'),

        # Create WholesaleApproval audit log
        migrations.CreateModel(
            name='WholesaleApproval',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('bill_snapshot',     models.JSONField(default=dict)),
                ('approved_by_name',  models.CharField(max_length=200)),
                ('created_at',        models.DateTimeField(auto_now_add=True)),
                ('area_manager', models.ForeignKey(
                    limit_choices_to={'role': 'AREAMANAGER'},
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='approvals_given',
                    to='pos.userprofile',
                )),
                ('sale', models.OneToOneField(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='approval',
                    to='pos.sale',
                )),
                ('store', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='wholesale_approvals',
                    to='pos.store',
                )),
                ('created_by', models.ForeignKey(
                    null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='+', to='auth.user',
                )),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
