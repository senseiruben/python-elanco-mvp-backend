
Tech stack choices:
Python -> I chose python as it was the language I am most familiar with for data processing,
I didn't want to overcomplicate the project, I am already familiar with a few of the libraries that I would be using
so it made python an easy pick.

Pandas -> I am using pandas for data ingestion and querying. This seemed like a pretty obvious option as I am already
slightly familiar with it and research showed me it is efficient for data consumption/ingestion. Alternatives like Dask
or PyArrow exist for data ingestion, but as there is a time constraint I wanted to avoid the unnecessary complexity.
I am also using this for storing my data as well as queries, I considered SQLite and SQLAlchemy, but it seemed overkill
to learn these tools and would extend the project unnecessarily when I can use In-memory storage. 

FastAPI -> I did some research into different frameworks, Django REST seemed like a good option, it scales well for large
projects and is well known, but it seemed overkill for a small MVP and also seemed like it would take up extra time. 
Flask is also small, lightweight and easy to learn, but my research showed FastAPI was more suited to my needs, it has
good performance and I can use FastAPIs build in Pyndantic integration for automatic data validation. 

Docker -> Used to ensure the project is easily run.

Uvicorn -> FastAPI is built on ASGI (asynchronous server gateway interface) and Uvicorn is an ASGI server meaning it
is the "default" lightweight server for FastAPI apps. Uvicorn is high-performance and simple to use, other ASGI
servers, such as hypercorn, required more setup and were over-complex for this task.