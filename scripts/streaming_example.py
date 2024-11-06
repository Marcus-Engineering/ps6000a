"""Sample program for PicoScope 6000E streaming mode."""
###############################################################################
# Project: PicoScope 6000E Driver
# File: streaming_example.py
#
# Sample program for PicoScope 6000E streaming mode.
#
# Copyright (c) 2024 Marcus Engineering, LLC (MIT Licensed)
#
#   Date      SCR  Comment                                        Eng
# -----------------------------------------------------------------------------
#   20210816       Created.                                       jrowley
#   20241105       Reworked to match styleof  block_example.py.   jrowley
#
###############################################################################

import time

try:
	import matplotlib.pyplot as plt
	import numpy as np
except ImportError:
	print("This example needs numpy and matplotlib, install [plot] extras.")
	raise


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
from ps6000a.types import PicoStreamingDataInfo

RATE = 10_000_000
RES = PicoDeviceResolution.DR_12BIT
CHAN = PicoChannel.CHANNEL_D
COUPL = PicoCoupling.DC
RANGE = PicoConnectProbeRange.X1_PROBE_2V
OFFSET = 0.0
SAMPS = 100_000
TARG_TIME = 1.0
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
ps.set_channel_on(
	channel=CHAN,
	coupling=COUPL,
	range_=RANGE,
	analog_offset=OFFSET,
	bandwidth=PicoBandwidthLimiter.BW_FULL,
)
ps.set_simple_trigger(
	enable=False,
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
# Sum of ``max_pre_trigger_samples`` and ``max_post_trigger_samples`` must
# be 64 or greater, or the API call will fail with an undocumented error
# code (0x7000).
interval = 1 / RATE
interval = ps.run_streaming(
	sample_interval=interval,
	max_pre_trigger_samples=SAMPS // 2,
	max_post_trigger_samples=SAMPS // 2,
	auto_stop=False,
	down_sample_ratio=2,
	down_sample_ratio_mode=PicoRatioMode.RAW,
)
print(f"true interval={interval}")
print(f"true rate={1/interval:.1f}Hz")

target_samples = int(TARG_TIME / interval)
total_samples = 0
result: np.ndarray = np.zeros(target_samples, dtype=RES.min_type.numpy_type)
run_time_start = time.perf_counter()
overflow = False

while total_samples < target_samples:
	full, sdia, _ = ps.get_streaming_latest_values()
	sdi: PicoStreamingDataInfo = sdia[0]

	# The REAL TRUTH about PicoStreamingDataInfo: What the manual says is
	# true, but there are a lot of omissions. start_index is indeed the
	# index of the first sample in the user-provided buffer, and
	# no_of_samples the number of samples made available... since the
	# last time GetStreamingLatestValues was called. So every time you call
	# the function you HAVE to retrieve or otherwise track the samples it
	# indicates are ready. Then if the function indicates that a new buffer
	# is needed (status code PICO_WAITING_FOR_DATA_BUFFERS, or in the OO
	# API first element of returned tuple is True), all of the above is
	# still true, but the buffer is also completely full, starting at the
	# very first index. And you need to load a new one to get more samples.

	# So for example here... if you just waited until full was True,
	# then you could set sa_start to 0 and sa_count to buffer.buffer.size.
	# And that probably is the more efficient way to do it anyways. But
	# just for demonstration we are really taking some samples every loop.
	sa_start = sdi.start_index
	sa_count = sdi.no_of_samples
	sa_count = min(sa_count, target_samples - total_samples)
	trim_buffer = np.array(buf.buffer)
	trim_buffer = trim_buffer[sa_start : sa_start + sa_count]
	result[total_samples : total_samples + sa_count] = trim_buffer
	total_samples += sa_count
	if full:
		ps.set_data_buffers(buf)
		print(".", end="")
	if sdi.overflow:
		overflow = True

run_time_end = time.perf_counter()
run_time = run_time_end - run_time_start
ps.close_unit()

print()
print(f"{run_time=}")
print(f"{TARG_TIME=}")
print(f"{total_samples=}")
if overflow:
	print("overflow")

plt.plot(
	np.linspace(0, interval * target_samples, target_samples),
	result / RES.min_type.max * RANGE.full_scale,
)
plt.show()
