"""Tests for some operations on a real PicoScope device."""
###############################################################################
# Project: PicoScope 6000E Driver
# File: test_ps6000a.py
#
# Tests for some operations on a real PicoScope device.
#
# Copyright (c) 2024 Marcus Engineering, LLC (MIT Licensed)
#
#   Date      SCR  Comment                                        Eng
# -----------------------------------------------------------------------------
#   20210816       Created.                                       jrowley
#
###############################################################################

import logging
from typing import Callable
import unittest

try:
	# noinspection PyUnresolvedReferences
	from ps6000a.constants import PicoDeviceResolution, PicoInfo, PicoStatus

	# noinspection PyUnresolvedReferences
	from ps6000a.exceptions import PicoStatusError

	# noinspection PyUnresolvedReferences
	from ps6000a.ps6000a import PS6000A

	# No problems, don't skip anything.
	def _import_skip(fn: Callable) -> Callable:
		return fn

except ImportError:

	# We can't exit the module gracefully, so we conditionally create this
	# decorator that will skip an entire test case if the imports fail.
	def _import_skip(fn: Callable) -> Callable:
		decorator = unittest.skip("Drivers not installed.")
		decorated = decorator(fn)
		return decorated


logger = logging.getLogger(__name__)


@_import_skip
class TestPicoScope6000A(unittest.TestCase):
	"""Tests for some operations on a real PicoScope device."""

	def __init__(self, methodName: str = "runTest") -> None:
		"""Initialize TestPicoScope6000A suite."""
		logging.basicConfig(level=logging.INFO)
		super().__init__(methodName)
		self._skip_all = False

	def setUp(self) -> None:
		"""Open PicoScope device."""
		if self._skip_all:
			raise unittest.SkipTest("Device not connected.")
		self.ps = PS6000A()
		try:
			assert self.ps.open_unit(None, PicoDeviceResolution.DR_8BIT)
		except PicoStatusError as e:
			if e.status == PicoStatus.NOT_FOUND:
				self._skip_all = True
				raise unittest.SkipTest("Device not connected.")
			else:
				raise e

	def tearDown(self) -> None:
		"""Close PicoScope device."""
		self.ps.close_unit()

	def test_aaa_unit_open(self) -> None:
		"""Test that unit was opened successfully (must be first test)."""
		if not isinstance(self.ps.last_status, PicoStatus):
			self.fail(
				f"last status is {self.ps.last_status.__class__}, not PicoStatus."
			)
		if self.ps.last_status != PicoStatus.OK:
			self.fail(f"Result of open_unit is {self.ps.last_status.name}.")
		if self.ps.raw_handle is None:
			self.fail("did not open scope.")
		elif self.ps.raw_handle < 0:
			self.fail("Could not open scope.")
		elif self.ps.raw_handle == 0:
			self.fail("Could not find scope.")
		logger.debug(f"Got valid handle to device: {self.ps.raw_handle}")

	def test_get_unit_info(self) -> None:
		"""Test getting each PicoInfo parameter from the live device."""
		info_items = [
			PicoInfo.DRIVER_VERSION,
			PicoInfo.USB_VERSION,
			PicoInfo.HARDWARE_VERSION,
			PicoInfo.VARIANT_INFO,
			PicoInfo.BATCH_AND_SERIAL,
			PicoInfo.CAL_DATE,
			PicoInfo.KERNEL_VERSION,
			PicoInfo.DIGITAL_HARDWARE_VERSION,
			PicoInfo.ANALOGUE_HARDWARE_VERSION,
			PicoInfo.FIRMWARE_VERSION_1,
			PicoInfo.FIRMWARE_VERSION_2,
			# PicoInfo.MAC_ADDRESS,
			# PicoInfo.SHADOW_CAL,
			PicoInfo.IPP_VERSION,
		]

		for info_code in info_items:
			try:
				string = self.ps.get_unit_info(info_code)
			except PicoStatusError:
				self.fail(
					f"Result of get_unit_info for {info_code.name} is "
					f"{self.ps.last_status.name}."
				)
			logger.info(f"{info_code.name} result: {string}")


if __name__ == "__main__":
	unittest.main()
