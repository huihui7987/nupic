# Copyright 2014 Numenta Inc.
#
# Copyright may exist in Contributors' modifications
# and/or contributions to the work.
#
# Use of this source code is governed by the MIT
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

import math

import numpy
from pyproj import Proj, transform
from nupic.encoders import CoordinateEncoder

try:
  import capnp
except ImportError:
  capnp = None
if capnp:
  from nupic.encoders.geospatial_coordinate_capnp import GeospatialCoordinateEncoderProto



# From http://spatialreference.org/ref/epsg/popular-visualisation-crs-mercator/
PROJ = Proj(init="epsg:3785")  # Spherical Mercator
PROJ_RANGE=(20037508.3428, 19971868.8804)  # in meters

# See http://gis.stackexchange.com/a/73829/41082
geocentric = Proj('+proj=geocent +datum=WGS84 +units=m +no_defs')


class GeospatialCoordinateEncoder(CoordinateEncoder):
  """
  Given a GPS coordinate and a speed reading, the
  Geospatial Coordinate Encoder returns an SDR representation
  of that position.

  :param: scale (int) Scale of the map, as measured by distance between two
          coordinates (in meters per dimensional unit)
  :param: timestep (int) Time between readings (in seconds)
  """

  def __init__(self,
               scale,
               timestep,
               w=21,
               n=1000,
               name=None,
               verbosity=0):
    super(GeospatialCoordinateEncoder, self).__init__(w=w,
                                                      n=n,
                                                      name=name,
                                                      verbosity=verbosity)

    self.scale = scale
    self.timestep = timestep


  def getDescription(self):
    """See `nupic.encoders.base.Encoder` for more information."""
    return [('speed', 0), ('longitude', 1), ('latitude', 2), ('altitude', 3)]


  def getScalars(self, inputData):
    """See `nupic.encoders.base.Encoder` for more information."""
    return numpy.array([0] * len(self.getDescription()))


  def encodeIntoArray(self, inputData, output):
    """
    See `nupic.encoders.base.Encoder` for more information.

    :param: inputData (tuple) Contains speed (float), longitude (float),
                             latitude (float), altitude (float)
    :param: output (numpy.array) Stores encoded SDR in this numpy array
    """
    altitude = None
    if len(inputData) == 4:
      (speed, longitude, latitude, altitude) = inputData
    else:
      (speed, longitude, latitude) = inputData
    coordinate = self.coordinateForPosition(longitude, latitude, altitude)
    radius = self.radiusForSpeed(speed)
    super(GeospatialCoordinateEncoder, self).encodeIntoArray(
     (coordinate, radius), output)


  def coordinateForPosition(self, longitude, latitude, altitude=None):
    """
    Returns coordinate for given GPS position.

    :param: longitude (float) Longitude of position
    :param: latitude (float) Latitude of position
    :param: altitude (float) Altitude of position
    :returns: (numpy.array) Coordinate that the given GPS position
                          maps to
    """
    coords = PROJ(longitude, latitude)

    if altitude is not None:
      coords = transform(PROJ, geocentric, coords[0], coords[1], altitude)

    coordinate = numpy.array(coords)
    coordinate = coordinate / self.scale
    return coordinate.astype(int)


  def radiusForSpeed(self, speed):
    """
    Returns radius for given speed.

    Tries to get the encodings of consecutive readings to be
    adjacent with some overlap.

    :param: speed (float) Speed (in meters per second)
    :returns: (int) Radius for given speed
    """
    overlap = 1.5
    coordinatesPerTimestep = speed * self.timestep / self.scale
    radius = int(round(float(coordinatesPerTimestep) / 2 * overlap))
    minRadius = int(math.ceil((math.sqrt(self.w) - 1) / 2))
    return max(radius, minRadius)


  def __str__(self):
    string = "GeospatialCoordinateEncoder:"
    string += "\n  w:   {w}".format(w=self.w)
    string += "\n  n:   {n}".format(n=self.n)
    return string


  @classmethod
  def getSchema(cls):
    return GeospatialCoordinateEncoderProto


  @classmethod
  def read(cls, proto):
    encoder = super(GeospatialCoordinateEncoder, cls).read(proto)
    encoder.scale = proto.scale
    encoder.timestep = proto.timestep
    return encoder


  def write(self, proto):
    super(GeospatialCoordinateEncoder, self).write(proto)
    proto.scale = self.scale
    proto.timestep = self.timestep
