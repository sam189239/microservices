import pika, json, os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "admin.settings")
django.setup()

from products.models import Product

params1 = pika.URLParameters('amqps://dcznnvcv:dO7K5YreWZG0ZjUkmuaJAiRwvRAGUH7F@puffin.rmq2.cloudamqp.com/dcznnvcv?heartbeat=65535')

connection = pika.BlockingConnection(params1)


channel = connection.channel()

channel.queue_declare(queue='admin')


def callback(ch, method, properties, body):
    print('Received in admin')
    id = json.loads(body)
    print(id)
    product = Product.objects.get(id=id)
    product.likes = product.likes + 1
    product.save()
    print('Product likes increased!')


channel.basic_consume(queue='admin', on_message_callback=callback, auto_ack=True)
print('Started Consuming')

channel.start_consuming()

#channel.close()
