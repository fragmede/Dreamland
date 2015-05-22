import zmq
import time
import sys
from random import randrange
from multiprocessing import Process

structureName = sys.argv[1]
serverIp = 'tcp://%s:' % sys.argv[2]

recv_port = '5560'
send_port = '5559'

context = zmq.Context()


def receiveMessageFromServer():
	topicFilter = '9'

	zmq_recv = context.socket(zmq.SUB)
	zmq_recv.connect(serverIp + recv_port)
	zmq_recv.setsockopt_string(zmq.SUBSCRIBE, topicFilter)

	counter = 1
	while True:
		stringRecv = zmq_recv.recv_string()
		topic, messageRecv = stringRecv.split(',')
		print('Received : ' + messageRecv + ' ' + str(counter) + ' times')
		counter += 1


def sendMessageToServer():
	send_zmq = context.socket(zmq.PUB)
	send_zmq.connect(serverIp + send_port)

	message = 'hello world'
	while True:
		topic = randrange(4, 10)
		print('Sending ' + str(topic))
		send_zmq.send_string('%i, %s' % (topic, message))
		time.sleep(1)


if __name__ == '__main__':
	Process(target=receiveMessageFromServer).start()
	Process(target=sendMessageToServer).start()