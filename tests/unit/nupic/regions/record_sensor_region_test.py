# Copyright 2015 Numenta Inc.
#
# Copyright may exist in Contributors' modifications
# and/or contributions to the work.
#
# Use of this source code is governed by the MIT
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
"""Unit tests for the RecordSensor region."""

import numpy
import os
import unittest2 as unittest

from nupic.engine import Network
from nupic.encoders import MultiEncoder
from nupic.data.file_record_stream import FileRecordStream



def _createNetwork():
  """Create network with one RecordSensor region."""
  network = Network()
  network.addRegion('sensor', 'py.RecordSensor', '{}')
  sensorRegion = network.regions['sensor'].getSelf()

  # Add an encoder.
  encoderParams = {'consumption': {'fieldname': 'consumption',
                                   'resolution': 0.88,
                                   'seed': 1,
                                   'name': 'consumption',
                                   'type': 'RandomDistributedScalarEncoder'}}

  encoder = MultiEncoder()
  encoder.addMultipleEncoders(encoderParams)
  sensorRegion.encoder = encoder

  # Add a data source.
  testDir = os.path.dirname(os.path.abspath(__file__))
  inputFile = os.path.join(testDir, 'fixtures', 'gymdata-test.csv')
  dataSource = FileRecordStream(streamID=inputFile)
  sensorRegion.dataSource = dataSource

  # Get and set what field index we want to predict.
  network.regions['sensor'].setParameter('predictedField', 'consumption')

  return network



class RecordSensorRegionTest(unittest.TestCase):
  """RecordSensor region unit tests."""


  def testVaryingNumberOfCategories(self):
    # Setup network with sensor; max number of categories = 2
    net = Network()
    sensorRegion = net.addRegion(
      "sensor", "py.RecordSensor", "{'numCategories': 2}")
    sensor = sensorRegion.getSelf()

    # Test for # of output categories = max
    data = {"_timestamp": None, "_category": [0, 1], "label": "0 1",
            "_sequenceId": 0, "y": 2.624902024, "x": 0.0,
            "_timestampRecordIdx": None, "_reset": 0}
    sensorOutput = numpy.array([0, 0], dtype="int32")
    sensor.populateCategoriesOut(data["_category"], sensorOutput)

    self.assertSequenceEqual([0, 1], sensorOutput.tolist(),
                             "Sensor failed to populate the array with record of two categories.")

    # Test for # of output categories > max
    data["_category"] = [1, 2, 3]
    sensorOutput = numpy.array([0, 0], dtype="int32")
    sensor.populateCategoriesOut(data["_category"], sensorOutput)

    self.assertSequenceEqual([1, 2], sensorOutput.tolist(),
                             "Sensor failed to populate the array w/ record of three categories.")

    # Test for # of output categories < max
    data["_category"] = [3]
    sensorOutput = numpy.array([0, 0], dtype="int32")
    sensor.populateCategoriesOut(data["_category"], sensorOutput)

    self.assertSequenceEqual([3, -1], sensorOutput.tolist(),
                             "Sensor failed to populate the array w/ record of one category.")

    # Test for no output categories
    data["_category"] = [None]
    sensorOutput = numpy.array([0, 0], dtype="int32")
    sensor.populateCategoriesOut(data["_category"], sensorOutput)

    self.assertSequenceEqual([-1, -1], sensorOutput.tolist(),
                             "Sensor failed to populate the array w/ record of zero categories.")


  def testBucketIdxOut(self):
    network = _createNetwork()
    network.run(1)  # Process 1 row of data
    bucketIdxOut = network.regions['sensor'].getOutputData('bucketIdxOut')[0]
    self.assertEquals(bucketIdxOut, 500)


  def testActValueOut(self):
    network = _createNetwork()
    network.run(1)  # Process 1 row of data
    actValueOut = network.regions['sensor'].getOutputData('actValueOut')[0]
    self.assertEquals(round(actValueOut, 1), 21.2)  # only 1 precision digit



if __name__ == "__main__":
  unittest.main()
