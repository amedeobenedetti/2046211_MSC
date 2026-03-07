import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='demo_exc',
                         exchange_type='topic')

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

print(f"queue_name = {queue_name}")

channel.queue_bind(exchange='demo_exc',
                   queue=queue_name,
                   routing_key='demo.#')

print(' [*] Waiting for logs. To exit press CTRL+C')

def callback(ch, method, properties, body):
    print(f" [x] {method.routing_key}:{body}")
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=False)


channel.start_consuming()