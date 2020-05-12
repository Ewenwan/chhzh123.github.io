---
layout: post
title: VS Code远端服务器(WSL/SSH)配置
tag: [configuration]
---

本文记录VS Code远端服务器(WSL/SSH)的配置方法。

<!--more-->

## WSL
需要在VS Code内安装远程服务器WSL插件，然后通过类似SSH的某种形式连接上服务器，接着就可以正常编辑了。

由于我安装TVM和深度学习库都在virtualenv的虚拟环境`pydev`内，所以还VS Code的项目中还需增添一个`.vscode/settings.json`文件，内容指明python位置。保存重新加载VS Code，可见左下角的Python解释器已改为对应的虚拟环境内的版本。同时为维持Python环境内的跳转功能，需要将一些插件禁用，之后VS Code会自动下载Microsoft的Language server，进而实现文件间跳转。

```json
{
    "python.venvPath": "/mnt/d/pydev",
    "python.pythonPath": "/mnt/d/pydev/bin/python",
    "python.linting.enabled": false,
    "python.jediEnabled": false
}
```

更多配置详情可见VS Code[官网文档](https://code.visualstudio.com/docs/python/environments#_where-the-extension-looks-for-environments)。

## SSH
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