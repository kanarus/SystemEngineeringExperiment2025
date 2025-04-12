from matplotlib import pyplot
from dataclasses import dataclass


@dataclass
class Point:
    """
    A data class representing a point in 2D space with x and y coordinates.
    """
    x: float
    y: float


class Plot:
    """
    A class representing a plot data with x and y float lists,
    where x is sorted in ascending order.
    """

    points: list[Point]

    title: str | None = None
    xlabel: str | None = None
    ylabel: str | None = None
    xlogscale: bool = False
    ylogscale: bool = False

    def __init__(
        self,
        x: list[float],
        y: list[float],
        title: str | None = None,
        xlabel: str | None = None,
        ylabel: str | None = None,
        xlogscale: bool = False,
        ylogscale: bool = False,
    ):
        if len(x) != len(y):
            raise ValueError("x and y must have the same length.")
        if len(x) == 0:
            raise ValueError("x and y must not be empty.")

        # Sort x and y based on the sorted order of x
        sorted_xys = sorted(zip(x, y), key=lambda pair: pair[0])
        self.points = [Point(xc, yc) for xc, yc in sorted_xys]

        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.xlogscale = xlogscale
        self.ylogscale = ylogscale

    def x(self) -> list[float]:
        """
        Return the x coordinates of the points in the plot.
        """
        return [point.x for point in self.points]
    def y(self) -> list[float]:
        """
        Return the y coordinates of the points in the plot.
        """
        return [point.y for point in self.points]

    def size(self) -> int:
        """
        Return the number of data points in the plot.
        """
        return len(self.points)
    
    def get(self, index: int) -> Point:
        """
        Return the point at the specified index.
        """

        if not index in range(0, self.size()):
            raise IndexError("Index out of range.")
        
        return self.points[index]
    
    def drop(self, index: int) -> None:
        """
        Remove the point at the specified index from the plot.
        This modifies the plot in place.
        """

        if not index in range(0, self.size()):
            raise IndexError("Index out of range.")
        
        del self.points[index]

    def figure(self) -> pyplot.Figure:
        """
        Create a matplotlib figure for the plot.
        """

        figure = pyplot.figure()

        if self.title is not None:
            pyplot.title(self.title)
        if self.xlogscale:
            pyplot.xscale('log')
        if self.ylogscale:
            pyplot.yscale('log')
        if self.xlabel is not None:
            pyplot.xlabel(self.xlabel)
        if self.ylabel is not None:
            pyplot.ylabel(self.ylabel)
        
        pyplot.grid()
        pyplot.scatter(x=self.x(), y=self.y(), s=8)
        
        return figure
