# Celery, Redis
from celery import shared_task
@shared_task
def process_data(data):
    # Process the data
    print(f"Processing data: {data}")