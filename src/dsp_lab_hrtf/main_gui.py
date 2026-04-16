import typing
from multiprocessing.synchronize import Event

if typing.TYPE_CHECKING:
    from matplotlib.artist import Artist
    from matplotlib.figure import Figure


class Gui:
    interval: int = 16

    def layout(self, fig: Figure, /):
        raise NotImplementedError()

    def setup(self) -> typing.Sequence[Artist]:
        return []

    def update(self, frame: int) -> typing.Sequence[Artist]:
        return []

    def main(self, stop: Event):
        import matplotlib
        from matplotlib import animation as anim
        from matplotlib import pyplot as plt

        matplotlib.rcParams["toolbar"] = "None"
        self.fig = plt.figure()
        self.fig.set_layout_engine("constrained")
        self.layout(self.fig)
        _ = anim.FuncAnimation(
            fig=self.fig,
            init_func=self.setup,
            func=self.update,
            interval=self.interval,
            cache_frame_data=False,
        )
        plt.show()
