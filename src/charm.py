#!/usr/bin/env python3
# Copyright 2022 Jon Seager
# See LICENSE file for licensing details.

"""Operator to control juju-introspect with systemd."""

import logging
from subprocess import CalledProcessError, check_call

from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, MaintenanceStatus

from jujuintrospect import JujuIntrospect

logger = logging.getLogger(__name__)


class JujuIntrospectCharm(CharmBase):
    """Operator to control juju-introspect with systemd."""

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.install, self._install)
        self.framework.observe(self.on.start, self._start)
        self.framework.observe(self.on.remove, self._remove)

        self.juju_introspect = JujuIntrospect()

        self.metrics_endpoint = MetricsEndpointProvider(
            self, jobs=[{"static_configs": [{"targets": ["*:6000"]}]}]
        )

    def _install(self, _):
        """Install the juju-introspect systemd unit."""
        self.unit.status = MaintenanceStatus("installing juju-introspect")
        self.juju_introspect.install()

    def _start(self, _):
        """Start the juju-introspect systemd unit."""
        self.juju_introspect.start()
        self._open_port()
        self.unit.status = ActiveStatus()

    def _remove(self, _):
        """Remove and stop the juju-introspect systemd unit."""
        self.unit.status = MaintenanceStatus("removing juju-introspect")
        self.juju_introspect.remove()

    def _open_port(self) -> bool:
        """Ensure that Juju opens the correct TCP port for juju-introspect."""
        try:
            check_call(["open-port", "6000/TCP"])
            return True
        except CalledProcessError as e:
            logger.error("error opening port: %s", str(e))
            logger.debug(e, exc_info=True)
            return False


if __name__ == "__main__":  # pragma: nocover
    main(JujuIntrospectCharm)
