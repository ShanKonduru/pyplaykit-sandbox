"""Device demo — a simulated smart thermostat (config/devices.yaml: demo-thermostat).

Run:  pytest tests/demo/functional/device -v                       # simulated twin (default)
      pytest tests/demo/functional/device --pyplaykit-dut-mode hil  # real device on
                                                                   # $PYPLAYKIT_DEMO_THERMOSTAT_PORT
Needs: pip install "pyplaykit[devices-serial]"
Inspect the bench:  pyplaykit devices list | show demo-thermostat | check
"""

import pytest

pytest.importorskip("serial", reason='the device demo needs: pip install "pyplaykit[devices-serial]"')

pytestmark = [pytest.mark.device, pytest.mark.requires_dut("demo-thermostat")]


def ask(dut, command: str, reply: str) -> str:
    console = dut.channel("console")
    console.clear()
    console.send(command + "\r\n")
    return console.expect(reply + r"=(\S+)", 5).group(1)


def test_reports_firmware_and_temperature(dut):
    assert ask(dut, "version", "FW") == "2.1.0"
    assert 5.0 <= float(ask(dut, "temp?", "TEMP")) <= 35.0


@pytest.mark.sim_only
def test_heats_towards_a_new_target(dut, sim_clock):
    console = dut.channel("console")
    console.clear()
    console.send("target 22\r\n")
    console.expect("OK", 5)
    sim_clock.advance(600)  # ten simulated minutes, no sleeping
    assert float(ask(dut, "temp?", "TEMP")) > 20.0


@pytest.mark.fault(kind="latency", delay=0.05)
def test_tolerates_a_slow_link(dut):
    assert ask(dut, "version", "FW") == "2.1.0"
