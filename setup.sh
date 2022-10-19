#!/usr/bin/env bash

echo "Removing existing versions..."
sudo apt purge bpfcc-tools libbpfcc python3-bpfcc -y

echo "Installing tools and dependencies..."
sudo apt install -y \
    python-is-python3 \
    bison \
    build-essential \
    cmake \
    flex \
    git \
    libedit-dev \
    libllvm11 \
    llvm-11-dev \
    llvm-dev \
    libclang-11-dev \
    libclang-dev \
    libclang-cpp-dev \
    zlib1g-dev \
    libelf-dev \
    libfl-dev \
    checkinstall \
    arping \
    clang-format \
    dh-python \
    dpkg-dev \
    pkg-kde-tools \
    ethtool \
    flex \
    inetutils-ping \
    iperf \
    libbpf-dev \
    libedit-dev \
    libzip-dev \
    linux-libc-dev \
    libluajit-5.1-dev \
    luajit \
    python3-netaddr \
    python3-pyroute2 \
    python3-distutils \
    python3

BCC_VERSION = "v0.25.0"
echo "Getting BCC "${BCC_VERSION}""

wget https://github.com/iovisor/bcc/releases/download/"${BCC_VERSION}"/bcc-src-with-submodule.tar.gz
tar xf bcc-src-with-submodule.tar.gz
cd bcc/ && mkdir build && cd build/
cmake -DCMAKE_INSTALL_PREFIX=/usr -DPYTHON_CMD=python3 ..
make
sudo checkinstall