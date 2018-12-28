# grpc python-client代码自动生成工具 #

## 说明
1. client目录用于存档生成的客户端代码
2. proto目录用于存放proto描述文件以及生成的py格式描述文件
3. tplate目录用于存放模板文件（主要包括需要导入的包模板、类定义模板、方法名称定义模板）
4. createGrpcClient.py用于启动生成客户端代码

## 注意
1. proto文件可以作为入参传入启动脚本的函数中，也可以直接将proto文件放入proto目录
2. 可执行tear_down函数清理所有代码自动生成的文件
