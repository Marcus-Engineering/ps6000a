"""Demonstrate block-mode acquisition with the PicoScope 6000E series."""
###############################################################################
# Project: PicoScope 6000E Driver
# File: block_example.py
#
# Demonstrate block-mode acquisition with the PicoScope 6000E series.
#
# Copyright (c) 2024 Marcus Engineering, LLC (MIT Licensed)
#
#   Date      SCR  Comment                                        Eng
# -----------------------------------------------------------------------------
#   20240314       Created.                                       jrowley
#
###############################################################################

import time

from ps6000a.constants import (
	PicoBandwidthLimiter,
	PicoChannel,
	PicoConnectProbeRange,
	PicoCoupling,
	PicoDeviceResolution,
	PicoRatioMode,
	PicoStatus,
	PicoThresholdDirection,
)
from ps6000a.ps6000a import PS6000A
from ps6000a.types import PicoHandle

RATE = 1_000_000
RES = PicoDeviceResolution.DR_12BIT
CHAN = PicoChannel.CHANNEL_C
COUPL = PicoCoupling.DC
RANGE = PicoConnectProbeRange.X1_PROBE_2V
OFFSET = 0.0
SAMPS = 100_000
TRIG_DIR = PicoThresholdDirection.FALLING
TRIG_THR = 0.1  # volts
TRIG_THR_CT = int(TRIG_THR / RANGE.full_scale * RES.min_type.max)

ps = PS6000A()
if not ps.open_unit(None, RES):
	print("Device not connected.")
	exit(-1)
if ps.last_status != PicoStatus.OK:
	print(f"Result of open_unit is {ps.last_status.name}.")
	exit(-1)
if ps.raw_handle is None or ps.raw_handle <= 0:
	print("Could not find/open scope.")
	exit(-1)

ps.set_channel_off(PicoChannel.CHANNEL_A)
ps.set_channel_off(PicoChannel.CHANNEL_B)
ps.set_channel_off(PicoChannel.CHANNEL_C)
ps.set_channel_off(PicoChannel.CHANNEL_D)
ps.clear_data_buffers(CHAN, PicoDeviceResolution.DR_12BIT.min_type, 0)

ps.set_channel_on(
	channel=CHAN,
	coupling=COUPL,
	range_=RANGE,
	analog_offset=OFFSET,
	bandwidth=PicoBandwidthLimiter.BW_FULL,
)
ps.set_simple_trigger(
	enable=True,
	source=CHAN,
	threshold=TRIG_THR_CT,
	direction=TRIG_DIR,
	delay=0,
	auto_trigger_micro_seconds=0,
)

buf = ps.get_data_buffer(
	channel=CHAN,
	n_samples=SAMPS,
	data_type=RES.min_type,
	segment=0,
	down_sample_ratio_mode=PicoRatioMode.RAW,
	clear_others=True,
)
ready = False
timebase, interval = ps.nearest_sample_interval_stateless(CHAN.flag, 1 / RATE, RES)
print(f"true rate: {1 / interval:.0f}Hz")


def callback(handle: PicoHandle, status: PicoStatus) -> None:
	"""
	Relay that data is ready.

	Callbacks are totally optional! You could poll with ``is_ready`` instead.
	"""
	global ready
	ready = True


ps.run_block(SAMPS // 2, SAMPS // 2, timebase, buf.segment, callback)

# while not ps.is_ready():  # if you didn't use a callback
while not ready:
	time.sleep(0.1)
	print(".", end="")
print("trig")

_, ovf = ps.get_values(0, SAMPS, 1, PicoRatioMode.RAW, buf.segment)
ps.close_unit()
if ovf:
	print("overflow")

try:
	import matplotlib.pyplot as plt
	import numpy as np
except ImportError:
	print("Won't plot, need numpy and matplotlib.")
else:
	plt.plot(
		np.linspace(-interval * (SAMPS // 2), interval * (SAMPS // 2), SAMPS),
		np.array(buf.buffer) / RES.min_type.max * RANGE.full_scale,
	)
	plt.show()
