from django.core.management.base import BaseCommand, CommandError
from articles.models import Publisher
import pandas as pd


class Command(BaseCommand):
    help = "Loads Publishers/Domains of publishers with reatings from a csv "

    def add_arguments(self, parser):
        parser.add_argument(
            "file_path",
            type=str,
            help="give the relative path of csv or a url of the csv",
        )

    def handle(self, *args, **options):
        file_path = options["file_path"]
        publishers = pd.read_csv(file_path)
        publisher_objs_create = []
        publisher_objs_update = []
        for domain, pc1 in zip(publishers["domain"], publishers["pc1"]):
            existing_publisher = Publisher.objects.filter(domain=domain).first()
            if existing_publisher:
                existing_publisher.pc1=pc1
                publisher_objs_update.append(existing_publisher)
            else:
                publisher_objs_create.append(Publisher(domain=domain, pc1=pc1))

        publishers_created = Publisher.objects.bulk_create(publisher_objs_create)
        publishers_updated = Publisher.objects.bulk_update(publisher_objs_update, fields=["pc1"])
        self.stdout.write(
            self.style.SUCCESS('Successfully created publishers "%s", updated publisher "%s"' % (publishers_created, publishers_updated))
        )
