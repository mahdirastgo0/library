from celery import shared_task

@shared_task(bind=True, rate_limit='3/m')
def process_order(self, order_data):
    try:
        # پردازش سفارش
    except Exception as e:
        self.retry(exc=e, countdown=60)