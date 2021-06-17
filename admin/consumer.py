import pika, json, os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "admin.settings")
django.setup()

from products.models import Product

params1 = pika.URLParameters('amqps://oenwuqee:91pzsvj2f941LHWu7ZY0-L9D5ojQ_v1K@snake.rmq2.cloudamqp.com/oenwuqee')

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
