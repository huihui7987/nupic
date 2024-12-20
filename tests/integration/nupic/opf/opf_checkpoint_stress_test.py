# Copyright 2013 Numenta Inc.
#
# Copyright may exist in Contributors' modifications
# and/or contributions to the work.
#
# Use of this source code is governed by the MIT
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

"""
This is a stress test that saves and loads an OPF checkpoint multiple times,
doing one compute step in between. This test was put in place to catch a crash
bug.
"""

import datetime
import numpy.random
import os
import shutil
import tempfile
import unittest2 as unittest

from nupic.frameworks.opf.model_factory import ModelFactory
from nupic.support.unittesthelpers.testcasebase import TestCaseBase

# Model parameters derived from the Hotgym anomaly example. This example was
# used because it uses the most components.  Some of the parameters, such
# as columnCount were reduced to make the test run faster.
MODEL_PARAMS = {
    'model': "HTMPrediction",
    'version': 1,
    'aggregationInfo': {  'days': 0,
        'fields': [(u'c1', 'sum'), (u'c0', 'first')],
        'hours': 1,
        'microseconds': 0,
        'milliseconds': 0,
        'minutes': 0,
        'months': 0,
        'seconds': 0,
        'weeks': 0,
        'years': 0},
    'predictAheadTime': None,
    'modelParams': {
        'inferenceType': 'TemporalAnomaly',
        'sensorParams': {
            'verbosity' : 0,
            'encoders': {
                u'consumption':    {  'clipInput': True,
                    'fieldname': u'consumption',
                    'maxval': 100.0,
                    'minval': 0.0,
                    'n': 50,
                    'name': u'c1',
                    'type': 'ScalarEncoder',
                    'w': 21},},
            'sensorAutoReset' : None,
        },
        'spEnable': True,
        'spParams': {
            'spVerbosity' : 0,
            'globalInhibition': 1,
            'spatialImp' : 'cpp',
            'columnCount': 512,
            'inputWidth': 0,
            'numActiveColumnsPerInhArea': 20,
            'seed': 1956,
            'potentialPct': 0.5,
            'synPermConnected': 0.1,
            'synPermActiveInc': 0.1,
            'synPermInactiveDec': 0.005,
        },
        'tmEnable' : True,
        'tmParams': {
            'verbosity': 0,
            'columnCount': 512,
            'cellsPerColumn': 8,
            'inputWidth': 512,
            'seed': 1960,
            'temporalImp': 'cpp',
            'newSynapseCount': 10,
            'maxSynapsesPerSegment': 20,
            'maxSegmentsPerCell': 32,
            'initialPerm': 0.21,
            'permanenceInc': 0.1,
            'permanenceDec' : 0.1,
            'globalDecay': 0.0,
            'maxAge': 0,
            'minThreshold': 4,
            'activationThreshold': 6,
            'outputType': 'normal',
            'pamLength': 1,
        },
        'clParams': {
            'regionName' : 'SDRClassifierRegion',
            'verbosity' : 0,
            'alpha': 0.005,
            'steps': '1,5',
        },

        'anomalyParams': {  u'anomalyCacheRecords': None,
    u'autoDetectThreshold': None,
    u'autoDetectWaitRecords': 2184},

        'trainSPNetOnlyIfRequested': False,
    },
}

class CheckpointStressTest(TestCaseBase):

  def testCheckpoint(self):
    tmpDir = tempfile.mkdtemp()
    model = ModelFactory.create(MODEL_PARAMS)
    model.enableInference({'predictedField': 'consumption'})
    headers = ['timestamp', 'consumption']

    # Now do a bunch of small load/train/save batches
    for _ in range(20):

      for _ in range(2):
        record = [datetime.datetime(2013, 12, 12), numpy.random.uniform(100)]
        modelInput = dict(zip(headers, record))
        model.run(modelInput)

      # Save and load a checkpoint after each batch. Clean up.
      tmpBundleName = os.path.join(tmpDir, "test_checkpoint")
      self.assertIs(model.save(tmpBundleName), None, "Save command failed.")
      model = ModelFactory.loadFromCheckpoint(tmpBundleName)
      shutil.rmtree(tmpBundleName)


if __name__ == "__main__":
  unittest.main()
