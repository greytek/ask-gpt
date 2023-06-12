#FROM python:3.10
#
#WORKDIR /ask-gpt
#COPY requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt
#COPY . .
#EXPOSE 8000
#ENV APP_HOST=0.0.0.0
#CMD ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"]




FROM python:3.9.4-slim

# Allow statements and log
ENV PYTHONUNBUFFERED True
# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./
# Install production dependencies.
RUN pip install -r requirements.txt
# Run
CMD ["python", "main.py"]
#
