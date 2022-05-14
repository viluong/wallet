FROM python:3.7
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /usr/app/wallet
COPY requirement.txt /usr/app/wallet/
RUN python -m pip install -U pip
RUN pip install -r requirement.txt

COPY . /usr/app/wallet/
