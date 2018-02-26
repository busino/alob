from .features import *

available_features = {NumPoints.name: NumPoints,
                      CoordinateStatistics.name: CoordinateStatistics,
                      Locations.name: Locations,
                      CenterOfGravity.name: CenterOfGravity,
                      Inertia.name: Inertia,
                      Position2dHistogramm3x3.name: Position2dHistogramm3x3,
                      PointMatching.name: PointMatching
                      }