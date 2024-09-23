FROM python:3.11-slim-bookworm
COPY app.py requirements.txt /
RUN pip install -r requirements.txt
EXPOSE 8080
CMD ["flask", "run", "-h", "0.0.0.0", "-p", "8080"]