FROM python:3.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY . .
RUN python -m pip install --upgrade pip \
  && pip install -r requirements.txt \
  && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
  && echo 'Asia/Shanghai' >/etc/timezone
EXPOSE 8000
#CMD ["python3 manage.py runserver 0.0.0.0:8000"]
CMD ["/usr/local/bin/python", "manage.py", "runserver" ,"0.0.0.0:80"]