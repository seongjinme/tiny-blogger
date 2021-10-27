FROM python:3.8

LABEL maintainer="Seongjin Hong <hongseongjin.to@gmail.com>"

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 80

ENV FLASK_APP blog
ENV FLASK_ENV production

ENTRYPOINT ["python"]

CMD ["-m", "flask", "run", "-h", "0.0.0.0"]