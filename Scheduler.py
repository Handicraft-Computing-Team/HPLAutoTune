import os


def open_avail_lists():

    # queues
    os.system('bqueues >> queues.txt')
    file = open("queues.txt", "r")
