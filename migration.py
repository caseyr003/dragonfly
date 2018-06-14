from plugins import ocic

# After we receive credentials from user we initialise a object.

# Authenticating and then saving in db.
def authenticate(arg):
    ret_obj,rc,status_msg = obj.authenticate()

# method to save the credentials in sqlite db
def insert_into_sqlite(arg):
    # insert_into_sqlite(obj.credentials)

# method to return list of instances
def list_instances(arg):
    ret_obj,rc,status_msg = obj.list()

# After the user confirms to migrate. We create a celery job and assign the job

def migrate(arg):
    celery = migrate_celery_task.delay(source, destination, instance_obj)
    # After this statement, the job is kicked off to backend and python
    # console moves on to next statement.
