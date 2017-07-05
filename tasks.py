# from celery import Celery
# from celery.schedules import crontab
# from celery.utils.log import get_task_logger
#
# logger = get_task_logger(__name__)
#
# celery_app = Celery('tasks', backend='mongodb://localhost:27017/fire2', broker='redis://localhost:6379/1')
#
# # @celery_app.on_after_configure.connect
# # def setup_periodic_tasks(sender, **kwargs):
# #     sender.add_periodic_task(30.0, test.s('world'), expires=10)
#
# @celery_app.task
def add(x, y):
    result = x + y
    print result
    return result


def minus(x, y):
    result = x - y
    print result
    return result

#
#
# @celery_app.task
# def test(arg):
#     print (arg)
