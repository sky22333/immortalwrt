#!/bin/bash

mkdir -p bin
chmod -R 755 bin
chmod +x build.sh
chmod +x files/etc/uci-defaults/99-custom.sh

docker run --rm -i \
-v ./bin:/home/build/immortalwrt/bin \
-v ./files/etc/uci-defaults:/home/build/immortalwrt/files/etc/uci-defaults \
-v ./build.sh:/home/build/immortalwrt/build.sh \
immortalwrt/imagebuilder:x86-64-openwrt-24.10.4 /home/build/immortalwrt/build.sh

# 查找对应架构的镜像：https://hub.docker.com/r/immortalwrt/imagebuilder/tags
