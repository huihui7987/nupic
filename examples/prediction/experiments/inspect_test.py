# Copyright 2013 Numenta Inc.
#
# Copyright may exist in Contributors' modifications
# and/or contributions to the work.
#
# Use of this source code is governed by the MIT
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

from nupic.engine import *
import os
import sys

os.chdir(sys.argv[1] + '/networks')

for name in ('trained_l1.nta', 'trained.nta'):
  if os.path.exists(name):
    break

n = Network(name)
n.inspect()
