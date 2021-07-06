FROM python:3.7
MAINTAINER Meditator_han<475641767@qq.com>
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
WORKDIR /code/zhongwen_novel
CMD ["scrapy","crawl","zwydw"]