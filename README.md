## immortalwrt构建脚本（image builder）

- 初始化脚本修改：[`files/etc/uci-defaults/99-custom.sh`](files/etc/uci-defaults/99-custom.sh)
- 内置软件包修改：[`build.sh`](build.sh)
- 镜像版本修改：[`docker-run.sh`](docker-run.sh)（选择符合自己设备的系统架构）

根据自己情况修改，修改后执行`docker-run.sh`脚本即可自动构建，构建出来的固件在当前路径`bin`目录。或者修改后运行Actions工作流自动编译。

#### 系统里在线扩容使用全部磁盘空间（仅限`x86/64`，`25.12+`，`ext4`镜像）

```
apk update
apk add parted losetup resize2fs blkid

wget -U "" -O expand-root.sh "https://openwrt.org/_export/code/docs/guide-user/advanced/expand_root?codeblock=0"

. ./expand-root.sh

sh /etc/uci-defaults/70-rootpt-resize
```
