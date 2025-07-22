from utils.logfire_related import logfire_configure

prefect_logfire = logfire_configure(local=True, service_name='prefect')
