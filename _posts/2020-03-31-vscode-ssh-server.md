---
layout: post
title: VS Code远端服务器配置
tag: [tools]
---

本文记录VS Code远端服务器的配置方法。

<!--more-->

下面所指的客户端都是自己的电脑，服务器端则是远端环境。

在客户端生成SSH key
```bash
ssh-keygen -t rsa -b 2048
```

通常生成在`C:\Users\your_name/.ssh/id_rsa`，将该文件的**内容**拷贝入服务器端的`~/.ssh/authorized_keys`，进而可实现免密SSH通信。

在客户端的VS Code安装[Remote - SSH](vscode:extension/ms-vscode-remote.remote-ssh)的插件。

在客户端的VS Code按F1，选择`Remote-SSH: Connect to Host`，输入`user@hostname`，其中`user`是你连接远端服务器所用的用户名，`hostname`是服务器的IP地址。

连接上后，VS Code会自动配置服务器端环境，默认会在服务器端下载并安装。如果你需要在本机下载好后再传送过去，则需要设置`remote.SSH.allowLocalServerDownload`（在文件->首选项->设置中），详情可参见[该文](https://code.visualstudio.com/docs/remote/faq#_what-are-the-connectivity-requirements-for-vs-code-server)。

## 参考资料
* Tutorial, <https://code.visualstudio.com/remote-tutorials/ssh/getting-started>
* Remote Development using SSH, <https://code.visualstudio.com/docs/remote/ssh>