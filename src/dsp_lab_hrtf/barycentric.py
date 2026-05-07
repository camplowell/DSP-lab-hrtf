from __future__ import annotations

import numpy as np
from scipy.spatial import ConvexHull
from sofar import Sofa
from tqdm import tqdm


class Triangle:
    indices: np.ndarray
    v0: np.ndarray
    v1: np.ndarray
    v2: np.ndarray
    _normal: np.ndarray
    # normal: np.ndarray
    d: float

    def __init__(self, positions: np.ndarray, indices: np.ndarray):
        self.indices = indices
        self.v0 = positions[indices[0]]
        self.v1 = positions[indices[1]]
        self.v2 = positions[indices[2]]
        self._normal = np.cross(self.v1 - self.v0, self.v2 - self.v0)
        self._normal /= np.dot(self._normal, self._normal)
        self.d = np.dot(self._normal, self.v0)

    def intersect(self, direction: np.ndarray) -> tuple[bool, np.ndarray]:
        """
        Project a point onto a triangle, returning the barycentric coordinate of said point if it intersects, or None if it doesn't.
        Ref: [Scratchapixel](https://www.scratchapixel.com/lessons/3d-basic-rendering/ray-tracing-rendering-a-triangle/barycentric-coordinates.html)
        """
        out = np.empty(3, dtype=np.float32)
        p_dot_n = np.dot(self._normal, direction)
        if np.abs(p_dot_n) < 1e-4:
            return False, out  # Nearly parallel
        t = self.d / p_dot_n
        if t < 0:
            return False, out  # Behind the origin
        P = t * direction

        C = np.cross(self.v2 - self.v1, P - self.v1)
        u = np.dot(self._normal, C)
        if u < -1e-4:
            return False, out  # Outide the tri on the u edge

        C = np.cross(self.v0 - self.v2, P - self.v2)
        v = np.dot(self._normal, C)
        if v < -1e-4:
            return False, out  # Outside the tri on the v edge

        C = np.cross(self.v1 - self.v0, P - self.v0)
        w = np.dot(self._normal, C)
        if w < -1e-4:
            return False, out  # Outside the tri on the w edge

        out[:] = u, v, (1 - u - v)
        return True, out


def bounds(*vectors: np.ndarray):
    all = np.stack(vectors)
    return all.min(axis=0), all.max(axis=0)


class VoxelPartition:
    """Used to test less than all the triangles for intersection. Assumes that:
    - triangles form a manifold shape
    - rays start at the origin
    - the origin is inside the shape
    - the shape is within the [-1, 1] range
    """

    resolution: int
    cells: list[list[list[list[Triangle]]]]

    def __init__(self, triangles: list[Triangle], resolution: int = 127):
        self.resolution = resolution
        self.cells = [
            [[[] for _ in range(resolution)] for _ in range(resolution)]
            for _ in range(resolution)
        ]
        for tri in tqdm(triangles, "Building acceleration structures"):
            verts = np.stack([tri.v0, tri.v1, tri.v2])
            tri_min, tri_max = np.min(verts, axis=0), np.max(verts, axis=0)
            tri_cell_min, tri_cell_max = self.cell(tri_min - 0.02), self.cell(tri_max)
            tri_cell_max = np.clip(tri_cell_max + 1, 0, resolution)
            for x in range(tri_cell_min[0], tri_cell_max[0]):
                for y in range(tri_cell_min[1], tri_cell_max[1]):
                    for z in range(tri_cell_min[2], tri_cell_max[2]):
                        if tri not in self.cells[x][y][z]:
                            self.cells[x][y][z].append(tri)

    def query(self, ray_dir: np.ndarray) -> list[Triangle]:
        # use DDA to trace through every cell the ray intersects, starting from 0
        result = []
        # ray_dir = ray_dir / np.linalg.norm(ray_dir)
        current = np.array([self.resolution // 2] * 3, dtype=int)
        step = np.sign(ray_dir).astype(int)
        cell_size = 2.0 / self.resolution

        t_max = np.full(3, float("inf"))
        t_delta = np.full(3, float("inf"))

        for i in range(3):
            if ray_dir[i] == 0:
                continue
            # World coordinate of current cell center
            cell_center = (
                current[i] - self.resolution // 2
            ) * cell_size + cell_size / 2
            # Distance to next cell boundary from origin
            t_max[i] = (cell_center + step[i] * cell_size / 2) / ray_dir[i]
            t_delta[i] = cell_size / abs(ray_dir[i])
        steps = 0
        # Traverse
        while True:
            if np.any(current < 0) or np.any(current >= self.resolution):
                break
            result.extend(self.cells[current[0]][current[1]][current[2]])
            axis = np.argmin(t_max)
            if t_max[axis] == float("inf"):
                break
            steps += 1
            current[axis] += step[axis]
            t_max[axis] += t_delta[axis]
        if len(result) == 0:
            print("Steps: ", steps)
            print("current:", current)
            print("t_delta:", t_delta)
            raise AssertionError()
        return result

    def cell(self, pos: np.ndarray):
        cells = np.empty_like(pos, dtype=np.intc)
        np.floor_divide(pos + 1, 2 / self.resolution, out=cells, casting="unsafe")
        return cells


class BarycentricEncoding:
    ir: np.ndarray
    positions: np.ndarray
    acceleration_structure: VoxelPartition
    last_tri: Triangle | None = None

    def __init__(self, hrtf: Sofa):
        self.ir = getattr(hrtf, "Data_IR")
        np.average(self.ir.var(axis=2))
        self.positions = cartesian(hrtf)
        hull = ConvexHull(self.positions)
        self.acceleration_structure = VoxelPartition(
            [Triangle(hull.points, tri) for tri in hull.simplices]
        )

    def query(self, pos: np.ndarray, gain: float = 1.0) -> np.ndarray:
        """Get the impulse response for the given position"""
        if self.last_tri:
            hit, wuv = self.last_tri.intersect(pos)
            if hit:
                wuv *= gain
                return (
                    wuv[0] * self.ir[self.last_tri.indices[0]]
                    + wuv[1] * self.ir[self.last_tri.indices[1]]
                    + wuv[2] * self.ir[self.last_tri.indices[2]]
                )
            else:
                self.last_tri = None

        candidates = self.acceleration_structure.query(pos)
        for tri in candidates:
            hit, wuv = tri.intersect(pos)
            if not hit:
                continue
            self.last_tri = tri
            wuv *= gain
            return (
                wuv[0] * self.ir[tri.indices[0]]
                + wuv[1] * self.ir[tri.indices[1]]
                + wuv[2] * self.ir[tri.indices[2]]
            )
        print(len(candidates))
        draw(pos, candidates)
        raise AssertionError("No intersections found!")


def cartesian(hrtf: Sofa) -> np.ndarray:
    """Speaker coordinates in cartesian coordinates"""
    azimuth_elevation: np.ndarray = getattr(hrtf, "SourcePosition")
    azimuth = np.deg2rad(azimuth_elevation[:, 0])
    elevation = np.deg2rad(azimuth_elevation[:, 1])
    radius = 1  # azimuth_elevation[:, 2]
    cartesian = np.ndarray(shape=azimuth_elevation.shape)
    cartesian[:, 0] = radius * np.cos(elevation) * np.cos(azimuth)
    cartesian[:, 1] = radius * np.cos(elevation) * np.sin(azimuth)
    cartesian[:, 2] = radius * np.sin(elevation)
    return cartesian


def draw(position: np.ndarray, triangles: list[Triangle]):
    from matplotlib import pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    verts = [np.stack([t.v0, t.v1, t.v2]) for t in triangles]

    poly = Poly3DCollection(verts, alpha=0.4, edgecolor="k", linewidth=0.5)
    poly.set_facecolor("steelblue")
    ax.add_collection3d(poly)

    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_zlim(-1, 1)

    ax.plot(*np.stack([[0, 0, 0], position]).T, color="red", linewidth=2)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    plt.tight_layout()
    plt.show()
