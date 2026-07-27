from django.db import migrations

def create_default_categories(apps, schema_editor):
    Category = apps.get_model('tools', 'Category')
    
    categories = [
        'Power Tools',
        'Hand Tools',
        'Gardening & Lawn',
        'Ladders & Scaffolding',
        'Cleaning & Pressure Washers',
    ]
    
    for cat_name in categories:
        Category.objects.get_or_create(name=cat_name)

def remove_default_categories(apps, schema_editor):
    Category = apps.get_model('tools', 'Category')
    Category.objects.filter(name__in=[
        'Power Tools',
        'Hand Tools',
        'Gardening & Lawn',
        'Ladders & Scaffolding',
        'Cleaning & Pressure Washers',
    ]).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0002_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_categories, remove_default_categories),
    ]