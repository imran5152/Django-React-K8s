from django.core.management.base import BaseCommand

from students.db import get_students_collection

SAMPLE_STUDENTS = [
    {"name": "Imran Pathan", "age": 20, "city": "Vaijapur"},
    {"name": "Aarav Deshmukh", "age": 19, "city": "Pune"},
    {"name": "Sneha Kulkarni", "age": 21, "city": "Aurangabad"},
    {"name": "Rohan Jadhav", "age": 20, "city": "Nashik"},
    {"name": "Meera Shaikh", "age": 22, "city": "Mumbai"},
]


class Command(BaseCommand):
    help = "Insert a few sample students if the collection is empty."

    def handle(self, *args, **options):
        students = get_students_collection()
        if students.count_documents({}) > 0:
            self.stdout.write("Students already exist. Nothing to do.")
            return
        students.insert_many([dict(student) for student in SAMPLE_STUDENTS])
        self.stdout.write(self.style.SUCCESS(f"Inserted {len(SAMPLE_STUDENTS)} students."))
