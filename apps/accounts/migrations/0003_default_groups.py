from django.db import migrations


def create_default_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    for name in ['Ops', 'Drivers', 'Merchants']:
        Group.objects.get_or_create(name=name)


def remove_default_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['Ops', 'Drivers', 'Merchants']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_merchant_webhookendpoint_user_flags'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_default_groups, remove_default_groups),
    ]
