# encoding=utf-8
# 实现模板生成工具
from string import Template
import os
import subprocess
import re
import linecache


class GenGrpcClient(object):
    def __init__(self, pb_path=''):
        # 生成初始化的pb以及prbc文件名称
        py_save_path = os.path.join(os.getcwd(), 'proto')
        pb_path_defalt = self.specify_file_format(fileformat='proto', fpath=py_save_path)[0]
        if pb_path:
            pb_file_path = pb_path
        else:
            pb_file_path = pb_path_defalt
        exe = 'python -m grpc_tools.protoc -I={} --python_out={} --grpc_python_out={} {}' \
            .format(py_save_path, py_save_path, py_save_path, pb_file_path)
        res_code = subprocess.check_call(exe)
        # print res_code
        # print pb_file_path
        # 修改py文件编码方式，首行添加编码格式描述文字
        file_list = self.specify_file_format(fileformat='py', fpath=os.getcwd() + '\\proto')
        # print 'success getting file_list {}'.format(file_list)
        for f in file_list:
            if f.split('\\')[-1] == '__init__.py':
                file_list.remove(f)
                # print 'new list is {}'.format(file_list)
            else:
                with open(f, 'r') as f1:
                    temp_file = f1.read()
                with open(f, 'w') as f1:
                    f1.writelines('# encoding=utf-8')
                    f1.writelines('\n')
                    f1.write(temp_file)
        # return pb_file_path, res_code

        pb_py_name_temp = os.path.splitext(pb_file_path.split('\\')[-1])[0]
        pb_py_name = '{}_pb2'.format(pb_py_name_temp)
        pb_grpc_py_name = '{}_pb2_grpc'.format(pb_py_name_temp)

        # 定义import相关的模板文件
        self.tempHead = os.path.join(os.getcwd() + '\\tplate', 'tempHead.txt')

        # import 类定义相关的模板文件
        self.tempClass = os.path.join(os.getcwd() + '\\tplate', 'tempClass.txt')

        # 定义类方法相关的模板文件
        self.tempFunc = os.path.join(os.getcwd() + '\\tplate', 'tempFunc.txt')

        # 定义测试代码中的main方法
        self.tempMain = os.path.join(os.getcwd() + '\\tplate', 'tempMain.txt')

        self.pb_py_name = pb_py_name

        self.pb_grpc_py_name = pb_grpc_py_name

    def specify_file_format(self, fileformat, fpath, use_child_dir=False):
        """
        定义一个从指定目录筛选指定格式文件的方法
        :param fileformat:
        :param fpath:
        :param use_child_dir:
        :return:
        """
        file_list = []
        # print '使用的目录为{}'.format(fpath)
        if use_child_dir:
            for root, dirs, files in os.walk(fpath):
                for filename in files:
                    if os.path.splitext(filename)[1] == '.' + fileformat:
                        # print 'file name is {}'.format(filename)
                        file_list.append(os.path.join(root, filename))
                    else:
                        print 'file format is {}'.format(os.path.splitext(filename)[1])
                        # print os.path.splitext(filename)[1]
        else:
            for root, dirs, files in os.walk(fpath):
                if root == fpath:
                    for filename in files:
                        if os.path.splitext(filename)[1] == '.' + fileformat:
                            # print 'file name is {}'.format(filename)
                            file_list.append(os.path.join(root, filename))
                        # else:
                        #     print 'file format is {}'.format(os.path.splitext(filename)[1])
                        # print os.path.splitext(filename)[1]
                else:
                    print 'root name is {}'.format(root)
        return file_list

    def get_keywords(self, word1, word2, file_path=''):
        """
        定义截取两个指定单词中间字段的方法
        :param word1:
        :param word2:
        :param file_path:
        :return:返回文件中所有满足条件的字段列表
        """
        if file_path:
            file_path = file_path
        else:
            file_path = os.path.join(os.getcwd() + '\\' + 'proto', self.pb_grpc_py_name + '.py')
        with open(file_path, 'r') as ff:
            # print 'grpc文件路径为{}'.format(os.path.join(os.getcwd() + '\\' + 'proto', pb_grpc_py_name + '.py'))
            # print '需要筛选类名的文件内容为{}'.format(ff.readlines())
            server_name = []
            if '.' in word1 or '.' in word2:
                word1.replace('.', '[.]')
                word2.replace('.', '[.]')
            search_word = ".*{}(.*){}.*".format(word1, word2)
            for line in ff.readlines():
                # print '每一行的内容为{}'.format(line)
                if re.search(search_word, line):
                    server_name = server_name + re.findall(search_word, line)
                    # server_name = re.findall("class(.*)\(object\)", line)
            server_name = [i.strip() for i in server_name]
            # print '替换结果为{}'.format(server_name)
            return server_name

    def get_header_para(self):
        """
        获取header文件替换参数
        :return:
        """
        header_para_dict = {'pbName': self.pb_py_name,
                            'pbGrpcName': self.pb_grpc_py_name}
        # print 'header文件可以替换的参数为{}'.format(header_para_dict)
        return header_para_dict

    def get_class_para(self):
        """
        获取 class文件替换参数
        :return:
        """
        grpc_server_name = self.get_keywords('class', '\(object\)')[0]
        class_para_dict = {'pbGrpcName': self.pb_grpc_py_name, 'serverName': grpc_server_name}
        # print '类定义文件可以替换的参数为{}'.format(class_para_dict)
        return class_para_dict

    def get_func_para(self):
        """
        获取Func文件中可以替换的方法名称
        :return:
        """
        grpc_server_name = self.get_keywords('class', '\(object\)')[0]
        word1_func = 'rb.' + grpc_server_name.split('Stub')[0] + '/'
        grpc_func_name = self.get_keywords(word1_func, '\'')
        func_input_para_dict = self.get_func_req_para(grpc_func_name)
        # print 'func_input_para_dict\'s value is {}'.format(func_input_para_dict)
        # print 'func_input_para_dict\'s type is {}'.format(type(func_input_para_dict))
        func_para_dict_list = []
        for i in grpc_func_name:
            # print para, type(para)
            # print 'k\'s value is {}'.format(i)
            para_dict_value = func_input_para_dict[i]
            para_dict = {'pbName': self.pb_py_name,
                         'funcName': i,
                         'para_dict': para_dict_value}
            func_para_dict_list.append(para_dict)
        # print '方法定义文件可以替换的参数为{}'.format(func_para_dict_list)
        return func_para_dict_list

    def get_func_req_para(self, func_para):
        pb_file = os.path.join(os.getcwd() + '\proto', self.pb_py_name + '.py')
        # print 'pb_file is {}'.format(pb_file)
        req_para_dict = {}
        for i in func_para:
            flag = 0
            res_para_key_list = []
            res_para_value_list = []
            # res_para_list = []
            all_line = linecache.getlines(pb_file)
            # print 'i is {}'.format(i)
            # 获取所有的参数名称
            for line in all_line:
                result = re.findall(".*{}Req[.](.*)',".format(i), line)
                flag -= 1
                if result:
                    # print 'result\'s value is {}'.format(result)
                    flag = 3
                    # print 'FLAG\'s value is {}'.format(FLAG)
                    res_para_key_list.append(result[0])
                if flag == 1:
                    para_value = re.findall(".*[ ]default_value=(.*),", line)
                    res_para_value_list.append(para_value[0])
                    # print '{}\'s default value is {}'.format(res_para_key_list[-1], para_value[0])
            # res_para_key_tuple = tuple(res_para_key_list)
            # res_para_value_tuple = tuple(res_para_value_list)
            res_para_kv = dict(map(lambda x, y: [x, y], res_para_key_list, res_para_value_list))
            # print 'res_para_list\' value is {}'.format(res_para_list)
            req_para_dict[i] = res_para_kv
        # print 'request para dict is {}'.format(req_para_dict)
        # print type(req_para_dict)
        return req_para_dict

    def genaral_client_code(self, file_name):
        """
        执行生成grpc python客户端代码操作
        :param file_name:
        :return:
        """
        header_para = self.get_header_para()
        class_para = self.get_class_para()
        func_para_list = self.get_func_para()
        os.chdir(os.getcwd()+'\\client')
        with open(file_name, 'w') as code:
            with open(self.tempHead, 'r') as header_file:
                for line in header_file.readlines():
                    s = Template(line)
                    new_line = s.substitute(header_para)
                    code.writelines(new_line)
            with open(self.tempClass, 'r') as class_file:
                code.writelines('\n')
                for line in class_file.readlines():
                    s = Template(line)
                    new_line = s.substitute(class_para)
                    code.write(new_line)
            for func_para in func_para_list:
                with open(self.tempFunc, 'r') as func_file:
                    code.writelines('\n')
                    for line in func_file.readlines():
                        s = Template(line)
                        new_line = s.substitute(func_para)
                        code.write(new_line)
            with open(self.tempMain, 'r') as main_file:
                code.writelines('\n')
                for line in main_file.readlines():
                    code.writelines(line)

    def tear_down(self):
        for root, dirs, files in os.walk(os.getcwd()+'\\proto'):
            for file in files:
                if os.path.splitext(file)[0] != '__init__':
                    # print os.path.join(root, file)
                    os.remove(os.path.join(root, file))
        for root, dirs, files in os.walk(os.getcwd()+'\\client'):
            for file in files:
                # print os.path.join(root, file)
                os.remove(os.path.join(root, file))


if __name__ == '__main__':
    newGenaral = GenGrpcClient()
    # grpc_server_name1 = newGenaral.get_keywords('class', '\(object\)')[0].split('Stub')[0]
    # grpc_client_name1 = 'grpc' + '_' + grpc_server_name1 + '_client.py'
    # newGenaral.genaral_client_code(grpc_client_name1)
    # 清理生成的客户端文件以及导入的proto文件
    newGenaral.tear_down()