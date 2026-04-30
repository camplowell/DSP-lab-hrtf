import numpy as np
from scipy.spatial import ConvexHull
from sofar import Sofa
from matplotlib import pyplot as plt


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

        simplices = self.convex_hull.simplices
        n = simplices.shape[0]
        out_simpl = [[]for _ in range(n)]
        #print(out_simpl)
        for s in range(0,n):
            [a, b, c] = simplices[s,:]
            
            out_simpl[a].append(s)
            out_simpl[b].append(s)
            out_simpl[c].append(s)
        self.facet_map = out_simpl



    def query(self, pos: np.ndarray) -> np.ndarray:
        """Get the impulse response for the given position"""
        #print('Query Runnin')
        pos = pos / np.linalg.norm(pos)
        #print(self.convex_hull.vertices)
        closest = np.argmax(np.vecdot(self.convex_hull.points, pos))
        #print(closest)
        potential_facets = self.facet_map[closest]
        #print(potential_facets)
        potential_facets_pt = self.convex_hull.simplices[potential_facets]
        #print(self.convex_hull.points[closest])
        #print('pot_face_pt:', potential_facets_pt)


        for facet in potential_facets_pt:
            v0, v1, v2 = [self.convex_hull.points[pt] for pt in facet]
            
            uv, reason = project(pos, v0, v1, v2)

            if uv is None:
                continue
            return (
                (1 - uv[0] - uv[1]) * self.hrir[facet[0]]
                + uv[0] * self.hrir[facet[1]]
                + uv[1] * self.hrir[facet[2]]
            )
        
        
        print(reason)
        fig = plt.figure()
        ax = fig.add_subplot(projection="3d")
        ax.scatter3D(*pos, color="green", s=60)  # pyright: ignore[reportArgumentType]
        
        ax.scatter3D(
            [v0[0],v1[0],v2[0]], [v0[1],v1[1],v2[1]], [v0[2],v1[2],v2[2]], color="red"
        )
        print(v0,v1,v2)
        ax.scatter3D(0,0,0, color="blue")
        ax.axis("equal")
        plt.show()
        

        raise AssertionError(
            "Point not in any neighboring simplex of the closest vertex!",
            potential_facets_pt
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
    reason = None
    #print('Project runnin')
    v0v1 = v1 - v0
    v0v2 = v2 - v0
    normal = np.cross(v0v1, v0v2)
    denom = np.dot(normal, normal)

    p_dot_n = np.dot(normal, point)

    if np.abs(p_dot_n) < 0.00001:
        return None, 'p_dot_n'

    d = -np.dot(normal, v0)
    t = -(d / p_dot_n)
    #print(d, t)
    if t < 0:
        return None, 't'  # Face is on the opposite side of the sphere

    # Query point, projected onto the triangle
    P = t * point

    # Calculate u
    v1p = P - v1
    v1v2 = v2 - v1
    C = np.cross(v1v2, v1p)
    u = np.dot(normal, C)
    if u+1e-10 < 0:
        return None, 'u'

    # Calculate v
    v2p = P - v2
    v2v0 = v0 - v2
    C = np.cross(v2v0, v2p)
    v = np.dot(normal, C)
    if v+1e-10 < 0:
        return None, 'v'

    v0p = P - v0
    C = np.cross(v0v1, v0p)
    w = np.dot(normal, C)
    if w+1e-10 < 0:
        return None, 'other'
    return (np.array([np.max(u,0), np.max(v,0)]) / denom), reason


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
