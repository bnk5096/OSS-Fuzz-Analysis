"""
File: ArcheoRun.py
Description: Runs the archeogit program (assuming it has been properly installed) for each project provided a file containing the issues for each project
Language: Python3 
"""

import os
import csv

projects = ['libarchive/libarchive', 'libass/libass', 'google/oss-fuzz', 'nlohmann/json', 'mm2/Little-CMS', 'file/file', 'randombit/botan', 'openssl/openssl', 'khaledhosny/ots', 'h2o/h2o', 'libimobiledevice/libplist', 'google/libprotobuf-mutator', 'grpc/grpc', 'libjpeg-turbo/libjpeg-turbo', 'google/brotli', 'google/guetzli', 'fosnola/libstaroffice', 'yaml/libyaml', 'strongswan/strongswan', 'OSGeo/gdal', 'OSGeo/PROJ', 'mstorsjo/fdk-aac', 'darktable-org/rawspeed', 'curl/curl', 'commonmark/cmark', 'uclouvain/openjpeg', 'uclouvain/openjpeg-data', 'rockdaboot/libpsl', 'open62541/open62541', 'resiprocate/resiprocate', 'openthread/openthread', 'glennrp/libpng', 'openthread/wpantund', 'curl/curl-fuzzer', 'wxWidgets/wxWidgets', 'VirusTotal/yara', 'chakra-core/ChakraCore', 'mozilla/gecko-dev', 'aawc/unrar', 'google/bloaty', 'llvm/llvm-project', 'boostorg/boost', 'ImageMagick/ImageMagick', 'irssi/irssi', 'systemd/systemd', 'libgd/libgd', 'google/wuffs', 'webmproject/libwebp', 'harfbuzz/harfbuzz', 'LibRaw/LibRaw', 'strukturag/libde265', 'envoyproxy/envoy', 'catenacyber/mbedtls', 'kjdev/hoextdown', 'mozilla/nestegg', 'capstone-engine/capstone', 'catenacyber/gnupg', 'obgm/libcoap', 'libexif/libexif', 'cherusker/freetype2-testing', 'openvswitch/ovs', 'libgit2/libgit2', 'cisco/openh264', 'OpenSC/OpenSC', 'GNUAspell/aspell', 'xiph/flac', 'radareorg/radare2', 'osquery/osquery', 'facebook/zstd', 'pauldreik/simdjson', 'ntop/nDPI', 'ethereum/solidity', 'lvandeve/lodepng', 'firebase/firebase-ios-sdk', 'samtools/htslib', 'mruby/mruby', 'WebAssembly/wabt', 'php/php-src', 'weinrank/usrsctp', 'danmar/cppcheck', 'google/AFL', 'MozillaSecurity/fuzzdata', 'lathiat/avahi', 'nanopb/nanopb', 'google/mtail', 'kkos/oniguruma', 'unicorn-engine/unicorn', 'mysql/mysql-server', 'libvips/libvips', 'libressl-portable/openbsd', 'dbry/WavPack', 'golang/go', 'openssh/openssh-portable', 'strukturag/libheif', 'NLnetLabs/unbound', 'apache/arrow', 'OISF/libhtp', 'Tencent/rapidjson', 'Cisco-Talos/clamav', 'catenacyber/elliptic-curve-differential-fuzzer', 'bytecodealliance/wasmtime', 'AOMediaCodec/libavif', 'meetecho/janus-gateway', 'nothings/stb', 'freetype/freetype2-testing', 'mozilla/mp4parse-rust', 'neomutt/neomutt', 'google/boringssl', 'hunspell/hunspell', 'GoogleCloudPlatform/esp-v2', 'c-ares/c-ares', 'ethereum/solidity-fuzzing-corpus', 'the-tcpdump-group/libpcap', 'DanBloomberg/leptonica', 'bellard/quickjs', 'PJK/libcbor', 'OISF/suricata', 'vstakhov/libucl', 'danielaparker/jsoncons', 'bytecodealliance/wasmtime-libfuzzer-corpus', 'guidovranken/cryptofuzz', 'git/git', 'janet-lang/janet', 'open-source-parsers/jsoncpp', 'haproxy/haproxy', 'zeromq/libzmq', 'google/gopacket', 'coredns/coredns', 'seladb/PcapPlusPlus', 'json-c/json-c', 'googleapis/go-genproto', 'python/cpython', 'rdkit/rdkit', 'facebook/hermes', 'tdewolff/parse', 'zlib-ng/zlib-ng', 'zeek/zeek', 'the-tcpdump-group/tcpdump', 'randy408/libspng', 'tdewolff/minify', 'prometheus/prometheus', 'guidovranken/cryptofuzz-corpora', 'vitessio/vitess', 'bytecodealliance/wasm-tools', 'buger/jsonparser', 'Blosc/c-blosc', 'qpdf/qpdf', 'libevent/libevent', 'mdempsky/go114-fuzz-build', 'beltoforion/muparser', 'WizardMac/ReadStat', 'zlib-ng/minizip-ng', 'dovecot/core', 'google/jsonnet', 'Blosc/c-blosc2', 'evverx/util-linux', 'util-linux/util-linux', 'tesseract-ocr/tesseract', 'AcademySoftwareFoundation/openexr', 'google/draco', 'OISF/suricata-verify', 'Mbed-TLS/mbedtls', 'arximboldi/immer', 'rnpgp/rnp', 'hugelgupf/p9', 'libyal/libfwnt', 'libyal/libolecf', 'libyal/libscca', 'libyal/libqcow', 'libyal/libvmdk', 'assimp/assimp', 'libyal/libfsapfs', 'libyal/libvhdi', 'libyal/libbde', 'libyal/libfsntfs', 'libyal/libfplist', 'google/fuzzing', 'libressl-portable/portable', 'uNetworking/uWebSockets', 'libyal/libfshfs', 'alembic/alembic', 'sleuthkit/sleuthkit', 'libyal/libfsext', 'libyal/libvslvm', 'libyal/libagdb', 'libyal/libmdmp', 'libyal/libewf', 'libsndfile/libsndfile', 'AFLplusplus/AFLplusplus', 'intel/libva', 'wolfSSL/wolfssl', 'sctplab/usrsctp', 'wolfSSL/wolfssh', 'fmtlib/fmt', 'rust-lang/regex', 'libyal/libesedb', 'yhirose/cpp-httplib', 'monero-project/monero', 'richgel999/miniz', 'ArashPartow/exprtk', 'apache/qpid-proton', 'GrokImageCompression/grok', 'google/flatbuffers', 'google/syzkaller', 'nats-io/nats-server', 'edenhill/librdkafka', 'libyal/libfsxfs', 'simdjson/simdjson', 'gohugoio/hugo', 'SerenityOS/serenity', 'clibs/clib', 'envoyproxy/go-control-plane', 'SELinuxProject/selinux', 'cesanta/mongoose', 'zyantific/zydis', 'pygments/pygments', 'mdbtools/mdbtools', 'istio/istio', 'ethereum/go-ethereum', 'Yubico/libfido2', 'trezor/trezor-firmware', 'secdev/scapy', 'igraph/igraph', 'tristanpenman/valijson', 'zeux/meshoptimizer', 'axboe/fio', 'mozilla/bleach', 'lua/lua', 'libssh2/libssh2', 'unicode-org/icu', 'microsoft/SymCrypt', 'tmux/tmux', 'relic-toolkit/relic', 'go-gitea/gitea', 'sudo-project/sudo', 'wolfSSL/wolfMQTT', 'fwupd/fwupd', 'civetweb/civetweb', 'LoupVaillant/Monocypher', 'p11-glue/p11-kit', 'imageio/imageio', 'mity/md4c', 'mz-automation/libiec61850', 'tats/w3m', 'LibreDWG/libredwg', 'nih-at/libzip', 'gpac/gpac', 'FasterXML/jackson-core', 'FasterXML/jackson-databind', 'FasterXML/jackson-dataformats-binary', 'lxc/lxc', 'jasper-software/jasper', 'libyal/libpff', 'catenacyber/fuzzpcap', 'kamailio/kamailio', 'eProsima/Fast-DDS', 'tinyobjloader/tinyobjloader', 'libyal/libmodi', 'FasterXML/jackson-dataformat-xml', 'Cyan4973/xxHash', 'wasm3/wasm3', 'linkerd/linkerd2-proxy', 'MikeMcl/bignumber.js', 'proftpd/proftpd', 'GrokImageCompression/grok-test-data', 'cosmos/cosmos-sdk', 'evanphx/json-patch', 'hyperium/h2', 'capnproto/capnproto', 'supranational/blst', 'libyal/libcreg', 'libyal/libvshadow', 'libyal/libregf', 'libyal/libfwevt', 'libyal/libodraw', 'espeak-ng/espeak-ng', 'bitcoin-core/qa-assets', 'bitcoin/bitcoin', 'ANSSI-FR/libecc', 'jhump/protoreflect', 'javaparser/javaparser', 'hyrise/sql-parser', 'znc/znc', 'videolan/vlc', 'libyal/libevtx', 'EsotericSoftware/kryo', 'pocoproject/poco', 'fribidi/fribidi', 'guidovranken/wolf-ssl-ssh-fuzzers', 'project-oak/oak', 'libjxl/libjxl', 'grpc/grpc-swift', 'dloebl/cgif', 'Unidata/netcdf-c', 'tendermint/tendermint', 'FasterXML/jackson-annotations', 'uber/h3', 'OpenVPN/openvpn', 'guidovranken/wolfmqtt-fuzzers', 'Chia-Network/bls-signatures', 'libyal/liblnk', 'stefanberger/libtpms', 'FRRouting/frr', 'htacg/tidy-html5', 'python-pillow/Pillow', 'containerd/containerd', 'google/OpenSK', 'net-snmp/net-snmp', 'celestiaorg/smt', 'Exiv2/exiv2', 'ARM-software/astc-encoder', 'libyal/libluksde', 'ClickHouse/ClickHouse', 'apache/httpd', 'taosdata/TDengine', 'zxing/zxing', 'KhronosGroup/SPIRV-Tools', 'apple/swift-protobuf', 'cisco/libsrtp', 'google/s2geometry', 'valyala/fasthttp', 'FreeRADIUS/freeradius-server', 'OpenSIPS/opensips', 'CESNET/libyang', 'arvidn/libtorrent', 'davea42/libdwarf-code', 'libbpf/libbpf', 'DavidKorczynski/binutils-preconditions', 'google/gson', 'yigolden/TiffLibrary', 'eclipse-cyclonedds/cyclonedds', 'alibaba/fastjson', 'sigstore/sigstore', 'cncf/cncf-fuzzing', 'django/django', 'google/gvisor', 'indutny/bn.js', 'libyal/libwrc', 'argoproj/argo-workflows', 'google/json5format', 'google/tcmalloc', 'argoproj/argo-events', 'RoaringBitmap/CRoaring', 'duckdb/duckdb', 'argoproj/argo-cd', 'etcd-io/etcd', 'bluez/bluez']


def read_file(filename):
    """
    Reads the specified file
    :param filename: the file to read from
    :return: data - a dictionary of collected issue information
    """

    data = {}
    with open(filename, encoding="utf8") as file:
        reader = csv.DictReader(file)
        for line in reader:
            data[line['id']] = line
    return data


def main():
    for project in projects:
        temp_name = project.replace("/", "___", project.count("/"))
        dir_name = temp_name.split("___")[-1]
        os.system("git clone https://github.com/" + project + ".git REPOSITORY_PATHS" + dir_name) # Configure paths
        data = read_file("data/" + temp_name + ".csv")
        counter = 0
        for entry in data:
            commit_hash = data[entry]['html'].split("/commit/")[-1]
	    temp_id = data[entry]['id']
            os.system("archeogit --config-file YAML_PATH blame --csv REPOSITORY_PATHS" + dir_name + " " + commit_hash + " > " + temp_name + str(temp_id) + ".csv") # Configure Paths
            counter += 1
        data.clear()
        os.system('rm -rf REPOSITORY_PATHS' + dir_name) # Configure Paths


if __name__ == '__main__':
    main()

