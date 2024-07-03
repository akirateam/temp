## Custom base image update

    # Latest updated release
    FROM ubi9/httpd-24

    # Switch to 'root' user to update and remove artifacts and modules
    USER root
    ENV container oci
    ENV PATH /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
    RUN dnf remove mod_ldap mod_session mod_security mod_auth_mellon -y
    RUN dnf install microdnf -y --setopt=install_weak_deps=0 --setopt=tsflags=nodocs
    RUN microdnf update -y --setopt=install_weak_deps=0 --setopt=tsflags=nodocs
    RUN [ ! -d /tmp/scripts ] || rm -rf /tmp/scripts
    RUN [ ! -d /tmp/artifacts ] || rm -rf /tmp/artifacts
    # Clear package manager metadata
    RUN microdnf clean all && yum clean all && dnf clean all
    RUN rm -rf /var/cache/yum /var/cache/dnf
    #rhbz 1609043
    RUN mkdir -p /var/log/rhsm

    # Tuning apache MPM Event
    COPY mpm_event.conf /etc/httpd/conf.d/
    # User
    USER 1001
    # Apache
    CMD ["/usr/bin/run-httpd"]
