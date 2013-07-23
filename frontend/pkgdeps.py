"""
List of distribution package dependencies for the frontend, that is,
packages needed for running the AFE and TKO servers
"""


from autotest.client.shared import distro


FEDORA_REDHAT_PKGS = [
    'Django',
    'Django-south',
    'MySQL-python',
    'git',
    'httpd',
    'java-devel',
    'mod_wsgi',
    'mysql-server',
    'numpy',
    'policycoreutils-python',
    'python-django',
    'python-atfork',
    'python-crypto',
    'python-httplib2',
    'python-imaging',
    'python-matplotlib',
    'python-paramiko',
    'selinux-policy',
    'selinux-policy-targeted',
    'tar',
    'unzip',
    'urw-fonts',
    'wget',
    'protobuf-compiler',
    'protobuf-python',
    'passwd',
    'pylint']


FEDORA_19_PKGS = [
    'MySQL-python',
    'git',
    'httpd',
    'java-1.7.0-openjdk-devel',
    'mod_wsgi',
    'mariadb-server',
    'numpy',
    'passwd',
    'policycoreutils-python',
    'protobuf-compiler',
    'protobuf-python',
    'pylint',
    'python-atfork',
    'python-crypto',
    'python-django14',
    'python-django-south',
    'python-httplib2',
    'python-pillow',
    'python-matplotlib',
    'python-paramiko',
    'selinux-policy',
    'selinux-policy-targeted',
    'tar',
    'unzip',
    'urw-fonts',
    'wget',
    ]


UBUNTU_PKGS = [
    'apache2-mpm-prefork',
    'git',
    'gnuplot',
    'libapache2-mod-wsgi',
    'makepasswd',
    'mysql-server',
    'openjdk-7-jre-headless',
    'python-crypto',
    'python-django',
    'python-django-south',
    'python-httplib2',
    'python-imaging',
    'python-matplotlib',
    'python-mysqldb',
    'python-numpy',
    'python-paramiko',
    'python-setuptools',
    'python-simplejson',
    'unzip',
    'wget',
    'protobuf-compiler',
    'python-protobuf',
    'pylint']


PKG_DEPS = {'fedora': FEDORA_REDHAT_PKGS,
            'redhat': FEDORA_REDHAT_PKGS,
            'ubuntu': UBUNTU_PKGS,
            distro.Spec('fedora', 19): FEDORA_19_PKGS}
