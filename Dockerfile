# syntax=docker/dockerfile:1

FROM ubuntu:20.04

ARG LLVM_VERSION="12"
ENV LLVM_VERSION=$LLVM_VERSION

ARG SHORTNAME="focal"

# Add llvm repo
RUN apt-get update && apt-get install -y curl gnupg &&\
    llvmRepository="\n\
deb http://apt.llvm.org/${SHORTNAME}/ llvm-toolchain-${SHORTNAME} main\n\
deb-src http://apt.llvm.org/${SHORTNAME}/ llvm-toolchain-${SHORTNAME} main\n\
deb http://apt.llvm.org/${SHORTNAME}/ llvm-toolchain-${SHORTNAME}-${LLVM_VERSION} main\n\
deb-src http://apt.llvm.org/${SHORTNAME}/ llvm-toolchain-${SHORTNAME}-${LLVM_VERSION} main\n" &&\
    echo $llvmRepository >> /etc/apt/sources.list && \
    curl -L https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add -

ARG DEBIAN_FRONTEND="noninteractive"
ENV TZ="Etc/UTC"

# Install dependencies and tools
RUN apt-get update && apt-get install -y \
      util-linux \
      bison \
      binutils-dev \
      cmake \
      flex \
      g++ \
      git \
      kmod \
      wget \
      libelf-dev \
      zlib1g-dev \
      libiberty-dev \
      libbfd-dev \
      libedit-dev \
      pkg-config \
      clang-${LLVM_VERSION} \
      libclang-${LLVM_VERSION}-dev \
      libclang-common-${LLVM_VERSION}-dev \
      libclang1-${LLVM_VERSION} \
      llvm-${LLVM_VERSION} \
      llvm-${LLVM_VERSION}-dev \
      llvm-${LLVM_VERSION}-runtime \
      libllvm${LLVM_VERSION} \
      libpcap-dev \
      gcc-multilib \
      systemtap-sdt-dev \
      sudo \
      iproute2 \
      python3 \
      python3-pip \
      ethtool \
      arping \
      netperf \
      iperf \
      iputils-ping \
      bridge-utils \
      libtinfo5 \
      libtinfo-dev \
      iperf \
      netperf \
      checkinstall \
      linux-headers-$(uname -r) \
      net-tools \
      pbuilder \
      aptitude && \
      apt-get -y clean

RUN pip3 install pyroute2==0.5.18 netaddr==0.8.0 dnslib==0.9.14 cachetools==3.1.1

RUN if [ ! -f "/usr/bin/python" ]; then ln -s /bin/python3 /usr/bin/python; fi
RUN if [ ! -f "/usr/local/bin/python" ]; then ln -s /usr/bin/python3 /usr/local/bin/python; fi

# Build BCC and install
RUN wget https://github.com/iovisor/bcc/releases/download/v0.25.0/bcc-src-with-submodule.tar.gz
RUN tar xf bcc-src-with-submodule.tar.gz
WORKDIR /bcc/build
RUN cmake -DCMAKE_INSTALL_PREFIX=/usr -DPYTHON_CMD=python3 ..
RUN make
RUN checkinstall

#Build XDP-Tools and libxdp
RUN apt-get install -y \
    clang \
    llvm \
    llvm-${LLVM_VERSION}-tools

WORKDIR /xdp-src
RUN git clone --recurse-submodules -j8 https://github.com/xdp-project/xdp-tools.git
WORKDIR /xdp-src/xdp-tools
RUN ./configure
RUN make

COPY simple-BPF-XDP ./examples