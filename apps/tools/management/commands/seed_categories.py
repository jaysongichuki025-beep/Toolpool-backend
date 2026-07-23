"""
═══════════════════════════════════════════════════════════════════════════
Management command: seed_categories
═══════════════════════════════════════════════════════════════════════════
WHY: Fresh databases have zero categories. This command inserts the defaults
so the browse page works immediately after docker compose up.

Run:  python manage.py seed_categories
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.tools.models import Category


DEFAULT_CATEGORIES = [
    ('Gardening', 'Lawn mowers, rakes, hedge trimmers, and outdoor gear.'),
    ('Power Tools', 'Drills, saws, sanders, and other electric tools.'),
    ('Hand Tools', 'Hammers, wrenches, screwdrivers, and basic kits.'),
    ('Automotive', 'Jack stands, wrenches, polishers for car work.'),
    ('Cleaning', 'Pressure washers, wet vacs, and deep-clean gear.'),
    ('Ladders & Access', 'Step ladders, extension ladders, scaffolding.'),
]


class Command(BaseCommand):
    help = 'Create default tool categories if they do not already exist'

    def handle(self, *args, **options):
        created_count = 0
        for name, description in DEFAULT_CATEGORIES:
            # get_or_create = insert only if missing (safe to re-run)
            obj, created = Category.objects.get_or_create(
                slug=slugify(name),
                defaults={'name': name, 'description': description, 'is_active': True},
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  + created: {name}'))
            else:
                self.stdout.write(f'  = exists: {name}')

        self.stdout.write(self.style.SUCCESS(f'Done. {created_count} new categories.'))
