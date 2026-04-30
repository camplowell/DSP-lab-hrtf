import numpy as np
from scipy.spatial import ConvexHull
from sofar import Sofa


class BarycentricInterpolator:
    def __init__(self, hrtf: Sofa):
        azimuth_elevation: np.ndarray = getattr(hrtf, "SourcePosition")
        azimuth = np.deg2rad(azimuth_elevation[:, 0])
        elevation = np.deg2rad(azimuth_elevation[:, 1])
        cartesian = np.ndarray(shape=azimuth_elevation.shape)
        cartesian[:, 0] = np.cos(elevation) * np.cos(azimuth)
        cartesian[:, 1] = np.cos(elevation) * np.sin(azimuth)
        cartesian[:, 2] = np.sin(elevation)
        self.convex_hull = ConvexHull(cartesian)
        self.hrir: np.ndarray = getattr(hrtf, "Data_IR")

    def query(self, pos: np.ndarray) -> np.ndarray:
        """Get the impulse response for the given position"""
        pos = pos / np.linalg.norm(pos)
        closest = np.argmax(np.vecdot(self.convex_hull.vertices, pos))
        potential_facets = self.convex_hull.neighbors[closest]
        for facet in potential_facets:
            v0, v1, v2 = [self.convex_hull.points[pt] for pt in facet]
            if (uv := project(pos, v0, v1, v2)) is None:
                continue
            return (
                (1 - uv[0] - uv[1]) * self.hrir[facet[0]]
                + uv[0] * self.hrir[facet[1]]
                + uv[1] * self.hrir[facet[2]]
            )

        raise AssertionError(
            "Point not in any neighboring simplex of the cosest vertex!"
        )


def dist(a: np.ndarray, b: np.ndarray):
    return np.linalg.norm(a - b)


def project(
    point: np.ndarray, v0: np.ndarray, v1: np.ndarray, v2: np.ndarray
) -> np.ndarray | None:
    """
    Project a point onto a triangle, returning the barycentric coordinate of said point if it intersects, or None if it doesn't.
    Ref: [Scratchapixel](https://www.scratchapixel.com/lessons/3d-basic-rendering/ray-tracing-rendering-a-triangle/barycentric-coordinates.html)
    """
    v0v1 = v1 - v0
    v0v2 = v2 - v0
    normal = np.cross(v0v1, v0v2)
    denom = np.dot(normal, normal)

    p_dot_n = np.dot(normal, point)
    if p_dot_n < 0.00001:
        return None

    d = -np.dot(normal, v0)
    t = -(d / p_dot_n)
    if t < 0:
        return None  # Face is on the opposite side of the sphere

    # Query point, projected onto the triangle
    P = t * point

    # Calculate u
    v1p = P - v1
    v1v2 = v2 - v1
    C = np.cross(v1v2, v1p)
    if (u := np.dot(normal, C)) < 0:
        return None

    # Calculate v
    v2p = P - v2
    v2v0 = v0 - v2
    C = np.cross(v2v0, v2p)
    if (v := np.dot(normal, C)) < 0:
        return None

    v0p = P - v0
    C = np.cross(v0v1, v0p)
    if np.dot(normal, C) < 0:
        return None

    return np.array([u, v]) / denom


if __name__ == "__main__":
    import argparse
    from importlib import resources
    from pathlib import Path

    parser = argparse.ArgumentParser(
        prog="hrtf",
        description="An implementation of head-related transfer functions",
    )
    parser.add_argument(
        "-a",
        "--audio",
        type=Path,
        help="The audio file to play; should be a PCM .wav file",
    )
    parser.add_argument(
        "-f",
        "--hrtf",
        type=Path,
        default=resources.files("dsp_lab_hrtf.data").joinpath(
            "mit_kemar_normal_pinna.sofa"
        ),
        help="The head-related transfer function to use; should be a '.sofa' file.",
    )
    args = parser.parse_args()
