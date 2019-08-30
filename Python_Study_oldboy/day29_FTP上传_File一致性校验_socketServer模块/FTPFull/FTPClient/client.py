import socket
import struct
import pickle
import hashlib
import os
import logging
import time

# {'action':'login','name':'user','password':'pwd'}
# {'action':'send_file',"file_path":'file_path','file_size':'file_size','file_md5_val':'file_md5_val'}
# {'action':'download_file','file_name':'file_name'}
# {'action':'return_code','code':'value'}
# 200:接受/发送 成功  201 校验失败  404 文件不存在 405 重发失败


class FtpClient():
    ClientFtp_mainPath = 'D:\\ClientFtp_mainPath'  # client客户端主目录
    user_log_ABSpath = None
    _file_suffix = '.dmp'

    def __init__(self, user, pwd, server_IP_PORT, user_mainpath=None):
        self.user = user
        self.pwd = pwd
        self.user_mainpath = user_mainpath  #不同用户的主目录
        # self.user_log_ABSpath = user_log_ABSpath
        self.server_IP_PORT = server_IP_PORT
        self.request = socket.socket()
        self.request.connect(server_IP_PORT)
        self.logger = None

    @staticmethod
    def get_logger(user):
        '''
            向用户目录中的log.txt中写入日志
        '''
        logger = logging.getLogger(user)

        handler_file = logging.FileHandler(
            FtpClient.user_log_ABSpath, mode='a+', encoding="utf-8")
        handler_stream = logging.StreamHandler()

        logger.setLevel(logging.DEBUG)
        handler_file.setLevel(logging.INFO)
        handler_stream.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s", datefmt="%d-%m-%Y %H:%M:%S")

        handler_file.setFormatter(formatter)
        handler_stream.setFormatter(formatter)

        logger.addHandler(handler_file)
        logger.addHandler(handler_stream)
        return logger

    @staticmethod
    def md5_encry(value, value_type='value'):
        md5_obj = hashlib.md5()
        if value_type == 'value':
            md5_obj.update(value.encode(encoding='utf-8'))
            return md5_obj.hexdigest()
        elif value_type == 'file_path':
            with open(value, mode='rb') as file_stream:
                for line in file_stream:
                    md5_obj.update(line)
                return md5_obj.hexdigest()

    def login(self, user, pwd):
        '''
        return 0 为登陆成功
        '''
        while True:
            self.send_head(action="login", name=user, password=pwd)
            head = self.recive_head()
            if head['action'] == 'return_code':
                recv_code = head['code']
                if recv_code == '0':
                    return 0
                elif recv_code == '1':
                    print('用户名错误，请重新输入')
                    user = input('请重新输入用户名：>>>>')
                    pwd = input('请重新输入密码：>>>>')
                    continue
                elif recv_code == '2':
                    pwd = input('密码错误，请重新输入密码：>>>>')
                    continue
                                                                                
    @classmethod
    def get_all_fileAbsPath(cls, path):
        file_lis = []
        if os.path.exists(path):
            while True:
                dir_lis = os.listdir(path)
                for item in dir_lis:
                    full_path = os.path.join(path, item)
                    if os.path.isfile(full_path):
                        file_lis.append(full_path)
                    elif os.path.isdir(full_path):
                        file_lis.extend(cls.get_all_fileAbsPath(full_path))
                break
        return file_lis

    def send_file_isdir_or_isfile(self, path):
        if os.path.isdir(path):
            all_fileAbsPath_lis = self.get_all_fileAbsPath(path)
            for item in all_fileAbsPath_lis:
                self.send_file(item)
        elif os.path.isfile(path):
            self.send_file(path)

    def send_file(self, file_path):
        times = 0
        while True:
            file_total_size = os.path.getsize(file_path)
            md5_val = self.md5_encry(file_path, value_type='file_path')
            self.send_head(action='send_file', file_path=file_path, file_size=file_total_size,
                           file_md5_val=md5_val)
            with open(file_path, mode='rb') as file_stream:
                for line in file_stream:
                    self.request.send(line)

            head = self.recive_head()
            if head['action'] == 'return_code':
                # recv = self.request.recv(1024).decode('gbk')
                if head['code'] == '200':
                    # self.request.close()
                    self.send_head(action='return_code', code='200')
                    break
                elif head['code'] == '201':
                    times += 1
                    if times < 6:
                        self.logger.debug('文件**%s**重发 %d 次。' %
                                               (file_path, times))
                        continue
                    else:
                        self.logger.info(
                            '文件**%s**重发次数超过5次，停止发送' % file_path)
                        self.send_head(action='return_code', code='405')
                        break

    def send_head(self, *arg, **args):
        if len(arg) != 0:
            head_pickle = pickle.dumps(arg[0])
            head_pickle_len = len(head_pickle)
            head_byte = struct.pack(
                'i%ds' % head_pickle_len, head_pickle_len, head_pickle)
            self.request.send(head_byte)
        elif len(args) != 0:
            head_dic = {}
            for k, v in args.items():
                head_dic[k] = v
            head_dic_pickle = pickle.dumps(head_dic)
            head_dic_pickle_len = len(head_dic_pickle)
            head_byte = struct.pack(
                'i%ds' % head_dic_pickle_len, head_dic_pickle_len, head_dic_pickle)
            self.request.send(head_byte)

    def recive_head(self):
        recv_head_len = self.request.recv(struct.calcsize('i'))  # return byet
        head_len = struct.unpack('i', recv_head_len)

        recv_head = self.request.recv(head_len[0])
        head = pickle.loads(recv_head)
        return head

    def recive_file(self, head):
        file_path = head['file_path']
        file_name = os.path.basename(file_path)
        local_file_path = os.path.join(self.user_mainpath, file_name)
        file_size = head['file_size']
        file_md5_val = head['file_md5_val']
        self.recive_data(local_file_path, file_size, file_md5_val)

    def recive_data(self, file_path, file_size, file_md5_val):
        has_recv_data_len = 0
        with open(file_path, mode='wb') as file_stream:
            while has_recv_data_len < file_size:
                recv_data = self.request.recv(1024)
                file_stream.write(recv_data)
                has_recv_data_len += len(recv_data)
                # print('%s文件总大小为%d，已接受%d' %
                #       (file_path, file_size, has_recv_data_len))
            if has_recv_data_len == file_size:  # and has_recv_data_len == file_size
                self.logger.debug('%s文件接收已完成' % file_path)
        local_file_md5_val = FtpClient.md5_encry(
            file_path, value_type='file_path')
        if local_file_md5_val == file_md5_val:
            self.logger.debug('%s文件校验已通过' % file_path)
            # print(os.path.abspath(file_path))
            self.send_head(action='return_code', code='200')
            # self.server.close_request(self.request)
            if os.path.splitext(file_path)[1] == self._file_suffix:
                self.logger.info('%s文件正常完成copy' % file_path)
                self.logger.debug('*' * 100)
        else:
            self.logger.debug('%s文件校验失败' % file_path)
            self.logger.debug('*' * 100)
            self.send_head(action='return_code', code='201')
            os.remove(file_path)


if __name__ == '__main__':
    user = input('请输入用户名：>>>>')
    pwd = input('请输入密码：>>>>')
    ip = input('请输入IP地址：>>>>')
    port = input('请输入端口号：>>>>')
    Ip_Port = (ip, int(port))
    ftp_client = FtpClient(user, pwd, Ip_Port)
    if ftp_client.login(user, pwd) == 0:
        ftp_client.user_mainpath = os.path.join(
            FtpClient.ClientFtp_mainPath, user)
        if not os.path.exists(ftp_client.user_mainpath):
            os.makedirs(ftp_client.user_mainpath)  # 在客户端为用户新建client用户目录
        FtpClient.user_log_ABSpath = os.path.join(
            ftp_client.user_mainpath, 'log.txt')  # 拼接客户端log.txt文件名
        ftp_client.logger = FtpClient.get_logger(user)
        ftp_client.logger.debug('登录成功，用户目录为：%s' % ftp_client.user_mainpath)
        while True:
            cmd = input('请输入操作命令>>>>')
            cmd_lis = cmd.strip().split(' ')
            if cmd_lis[0] == 'update':
                file_path = cmd_lis[1]
                if os.path.exists(file_path):
                    ftp_client.send_file_isdir_or_isfile(file_path)
                    continue
                else:
                    ftp_client.logger.debug('路径不存在,请确认后重新输入......')
            elif cmd_lis[0] == 'download':
                file_path = cmd_lis[1]
                ftp_client.send_head(
                    action='download_file', file_path=file_path)
                while True:
                    head = ftp_client.recive_head()
                    if head['action'] == 'return_code':
                        if head['code'] == '404':
                            ftp_client.logger.debug('文件名不存在,请重新选择文件进行下载')
                            file_path = input('请重新输入需要下载的文件名>>>>')
                            ftp_client.send_head(
                                action='download_file', file_path=file_path)
                        elif head['code'] == '405':
                            break
                        elif head['code'] == '200':
                            break
                    elif head['action'] == 'send_file':
                        ftp_client.recive_file(head)
                        continue
                continue
            elif cmd_lis[0] == 'dir':
                ftp_client.send_head(action='dir_all_file')
                all_file_lis = ftp_client.recive_head()
                for item in all_file_lis:
                    ftp_client.logger.debug('file_name:**%s**|file_size:**%s**' %
                                            (item["file_name"], item["file_size"]))
                    ftp_client.logger.debug('*' * 50)
                continue
            elif cmd_lis[0] == 'exit':
                ftp_client.send_head(
                    action='exit')
                ftp_client.request.close()
                ftp_client.logger.debug('用户**%s**退出' % ftp_client.user)
                break
            else:
                string = '''
                可使用命令如下：
                    1、update file_Abs_path
                    2、downlo file_name
                    3、dir
                    4、exit
                '''
                print(string)
        # ret = send_head(a='1', b=2, c="3")
        # print(ret)
