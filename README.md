# scrapy-docker

## 使用scrapy抓取中文阅读网的排行榜内的全部小说完本（含Dockerfile可远程部署）

#### 项目运行

> 下载代码

- git clone [git@github.com](mailto:git@github.com)/MrShowhan/scrapy-docker.git

> 安装依赖

- pip install -r requirements.txt

> 配置修改

- setting.py 指定redis数据库及mongodb数据库的连接参数

  ```
  MONGO_HOST = 'localhost'
  MONGO_PORT = 27017
  MONGO_USER = 'root'
  # MONGO_PASSWORD = 'xxxxx'
  
  REDIS_HOST = 'localhost'
  REDIS_PORT = 6379
  # REDIS_PASSWORD = 'xxxxx'
  REDIS_INDEX = 0
  ```

> 启动项目

- 本地启动程序：切换目录至 ../mydocker/zhongwen_novel 后执行`scray crawl zwydw`开始程序。开启后会自动爬取所有排行榜上的全本小说至mongodb数据库中的novel中，后续会上传添加附件程序（把小说转化成txt格式）

- docker远程部署：先把mydocker这个文件发送到远程服务器上（需要提前安装Docker），切换至改目录上使用一下代理进行镜像创建：

  #镜像名称 自行定义

  ```
  docker build -t #镜像名称 .
  ```

  启动镜像：

  镜像名称为上面自定义的名称

  #容器名 自行定义

  ```
  docker run -it --name容器名 镜像名称 /bin/bash
  ```

  进入容器内部后再执行`scray crawl zwydw`开启程序

