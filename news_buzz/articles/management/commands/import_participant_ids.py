# Inside a new file your_app/management/commands/import_participant_ids.py

from django.core.management.base import BaseCommand
import csv
from articles.models import Participant

class Command(BaseCommand):
    help = 'Import participant IDs from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('test_participant_ids.csv', type=str, help='/Users/admin/Documents/news_buzz/test_participant_ids.csv')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['test_participant_ids.csv']

        with open(csv_file_path, 'r') as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip the header

            for row in reader:
                participant_id = row[0]
                Participant.objects.create(participant_id=participant_id)

            self.stdout.write(self.style.SUCCESS('Successfully imported participant IDs'))
