from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import pos.models


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        # Add AREAMANAGER role + phone to UserProfile
        migrations.AddField(
            model_name='userprofile',
            name='phone',
            field=models.CharField(blank=True, max_length=20,
                                   help_text='Mobile number for OTP (Area Managers)'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(
                choices=[
                    ('SUPERADMIN',   'Super Admin'),
                    ('OWNER',        'Store Owner'),
                    ('STAFF',        'Staff'),
                    ('AREAMANAGER',  'Area Manager'),
                ],
                default='STAFF', max_length=20
            ),
        ),

        # AreaManagerStore
        migrations.CreateModel(
            name='AreaManagerStore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('assigned_at', models.DateTimeField(auto_now_add=True)),
                ('manager', models.ForeignKey(
                    limit_choices_to={'role': 'AREAMANAGER'},
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='managed_stores',
                    to='pos.userprofile',
                )),
                ('store', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='area_managers',
                    to='pos.store',
                )),
                ('assigned_by', models.ForeignKey(
                    null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='+', to='auth.user',
                )),
            ],
            options={'ordering': ['store__name', 'manager__user__username'],
                     'unique_together': {('manager', 'store')}},
        ),

        # WholesaleOTP
        migrations.CreateModel(
            name='WholesaleOTP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('otp_code',      models.CharField(max_length=6, default=pos.models._otp_default)),
                ('bill_snapshot', models.JSONField(default=dict)),
                ('status',        models.CharField(
                    choices=[('PENDING','Pending'),('VERIFIED','Verified'),
                             ('EXPIRED','Expired'),('FAILED','Failed')],
                    default='PENDING', max_length=10,
                )),
                ('attempts',    models.PositiveSmallIntegerField(default=0)),
                ('created_at',  models.DateTimeField(auto_now_add=True)),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('expires_at',  models.DateTimeField()),
                ('area_manager', models.ForeignKey(
                    limit_choices_to={'role': 'AREAMANAGER'},
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='issued_otps', to='pos.userprofile',
                )),
                ('store', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='wholesale_otps', to='pos.store',
                )),
                ('created_by', models.ForeignKey(
                    null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='+', to='auth.user',
                )),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
