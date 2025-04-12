class Plot:
    """
    A class representing a plot data with x and y float lists,
    where x is sorted in ascending order.
    """

    x: list[float]
    y: list[float]

    def __init__(self, x: list[float], y: list[float]):
        if len(x) != len(y):
            raise ValueError("x and y must have the same length.")
        if len(x) == 0:
            raise ValueError("x and y must not be empty.")

        # Sort x and y based on the sorted order of x
        sorted_pairs = sorted(zip(x, y), key=lambda pair: pair[0])
        self.x, self.y = map(list, zip(*sorted_pairs))

    def size(self) -> int:
        """
        Return the number of data points in the plot.
        """
        return len(self.x)
    
    def drop_by_index(self, index: int) -> None:
        """
        Drop the data at the given index from both x and y.
        """

        if not index in range(0, self.size()):
            raise IndexError("Index out of range.")
        
        del self.x[index]
        del self.y[index]
