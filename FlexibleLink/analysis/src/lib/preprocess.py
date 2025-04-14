from lib.plot import Plot, Point

import math


def by_y_increase_continuity(
    p: Plot,
    THRESHOLD_INCREATE_CHANGE_RATE: float = 3 # [unit]
) -> int:
    # Convert scaled coordinates to linear for the outlier detection
    if p.xlogscale:
        p.points = [Point(math.log10(point.x), point.y) for point in p.points]
    if p.ylogscale:
        p.points = [Point(point.x, math.log10(point.y)) for point in p.points]
    
    outliers = []
    for i in range(2, p.size()):
        prev2, prev1, this = p.get(i-2), p.get(i-1), p.get(i)
        y_diff, prev_y_diff = this.y - prev1.y, prev1.y - prev2.y
        if y_diff > 0 and abs(y_diff / prev_y_diff) > THRESHOLD_INCREATE_CHANGE_RATE:
            outliers.append(i)

    dropshift = 0
    for i in outliers:
        print(f"dropping {i} (obvoius outlier)")
        p.drop(i - dropshift)
        dropshift += 1

    # Restore the original scale of the coordinates
    if p.xlogscale:
        p.points = [Point(10**point.x, point.y) for point in p.points]
    if p.ylogscale:
        p.points = [Point(point.x, 10**point.y) for point in p.points]

    return len(outliers)


def amplify_valleys(
    p: Plot,
    THRESHOLD_DROP_RATE: float = 5, # [unit]
    EXPECTED_VALLEY_COUNT: int = 1, # [unit]
) -> None:
    print(f"amplifying valleys in {p.title}...")
    
    # Convert scaled coordinates to linear for the outlier detection
    if p.xlogscale:
        p.points = [Point(math.log10(point.x), point.y) for point in p.points]
    if p.ylogscale:
        p.points = [Point(point.x, math.log10(point.y)) for point in p.points]
    
    valley_count = 0
    for i in range(1, p.size() - 1):
        prev, this, next = p.get(i-1), p.get(i), p.get(i+1)
        if prev.y > this.y and this.y < next.y and (prev.distance(this) / prev.distance(next)) > THRESHOLD_DROP_RATE and (next.distance(this) / prev.distance(next)) > THRESHOLD_DROP_RATE:
            print(f"valley found at {i} ({this.x}, {this.y})")
            valley_count += 1
            for i in range(0, p.size() // ((EXPECTED_VALLEY_COUNT + 1) * 3)):
                p.insert(i, Point(this.x + 0.001 * i, this.y - i * 2.0))
            if valley_count >= EXPECTED_VALLEY_COUNT:
                break

    # Restore the original scale of the coordinates
    if p.xlogscale:
        p.points = [Point(10**point.x, point.y) for point in p.points]
    if p.ylogscale:
        p.points = [Point(point.x, 10**point.y) for point in p.points]


def by_vec_angle_continuity(
    p: Plot,
    THRESHOLD_RADIANS: float = math.pi / 12 # [rad], 15 degrees
) -> None:
    """
    In-place filter of the points in `p` based on the continuity of the angle
    between the vectors formed by consecutive points.
    """

    by_y_increase_continuity(p)

    # Convert scaled coordinates to linear for the outlier detection
    if p.xlogscale:
        p.points = [Point(math.log10(point.x), point.y) for point in p.points]
    if p.ylogscale:
        p.points = [Point(point.x, math.log10(point.y)) for point in p.points]

    i = 2 # assuming the first two points (index 0, 1) are not outliers
    while i < p.size():
        this, prev1, prev2 = p.get(i), p.get(i-1), p.get(i-2)

        # Compare the angles of two vectors:
        # 
        # - `prev_vec` : prev2 -> prev1
        # - `this_vec` : prev1 -> this
        # 
        # If the difference of the angles is greater than a threshold,
        # (i.e. the angle is not continuous, this poits makes a non-smooth part)
        # there's two possibilities:
        # 
        # 1. this point is an outlier
        # 2. this is the first point of a new curve
        # 
        # When 1., we remove this point.
        # When 2., we keep this point and go to the next point.

        prev_vec_radians = math.atan2(prev1.y - prev2.y, prev1.x - prev2.x)
        this_vec_radians = math.atan2(this.y - prev1.y, this.x - prev1.x)
        
        if abs(this_vec_radians - prev_vec_radians) < THRESHOLD_RADIANS:
            i += 1
        else:
            # Check if this point is an outlier (case 1.).
            # 
            # 1. When `this` is the final point of the curve,
            #    `this` will be an outlier and we should remove `this`.
            # 2. When `this` is NOT the final point of the curve,
            #    we introduce `next`, the next point of `this`, and:
            #    
            #    - `next_vec` : this -> next
            #    - `skip_vec` : prev1 -> next
            #    
            #    a. If the angle of `skip_vec` is continuous with `prev_vec`,
            #       `this` can be considered as an outlier.
            #    b. If the angle of `skip_vec` is NOT continuous with `prev_vec`,
            #
            #        p. If the angle of `next_vec` is continuous with `this_vec`,
            #           `this`, `next`, `next2` will be the first points of a new curve.
            #        q. If the angle of `next_vec` is NOT continuous with `this_vec`,
            #           we introduce `next2`, the next point of `next` (if cannot,
            #           i.e. `next` is the final point of the curve, we can consider
            #           both `this` and `next` as outliers, and remove them), and:
            #
            #           - `next2_vec` : next -> next2
            #           - `skip2_vec` : this -> next2
            #           
            #           x. If the angle of `skip2_vec` is continuous with `this_vec`,
            #              `this` and `next2` will be the first points of a new curve,
            #              and `next` will be an outlier.
            #           y. If the angle of `skip2_vec` is NOT continuous with `this_vec`,
            #              
            #              - If `skip2_vec` is continuous with `next_vec`,
            #                `next` and `next2` will be the first points of a new curve,
            #                and `this` will be an outlier.
            #              - If `skip2_vec` is NOT continuous with `next_vec`,
            #                go to the next point.

            if i == p.size() - 1:
                p.drop(i)
            else:
                next = p.get(i + 1)

                skip_vec_radians = math.atan2(next.y - prev1.y, next.x - prev1.x)
                next_vec_radians = math.atan2(next.y - this.y, next.x - this.x)

                if abs(skip_vec_radians - prev_vec_radians) < THRESHOLD_RADIANS:
                    p.drop(i) # `this` is an outlier
                    i += 1    # skip `next`, obviously not an outlier because of the continuity
                elif abs(next_vec_radians - this_vec_radians) < THRESHOLD_RADIANS:
                    i += 2    # skip `this` and `next`, both are the first points of a new curve
                else:
                    if i == p.size() - 2:
                        p.drop(i) # `this` is an outlier
                        p.drop(i) # `next` is an outlier
                    else:
                        next2 = p.get(i + 2)

                        skip2_vec_radians = math.atan2(next2.y - this.y, next2.x - this.x)
                        next2_vec_radians = math.atan2(next2.y - next.y, next2.x - next.x)

                        if abs(skip2_vec_radians - skip_vec_radians) < THRESHOLD_RADIANS:
                            p.drop(i + 1) # `next` is an outlier
                            i += 2        # skip `next2`, obviously not an outlier because of the continuity
                        elif abs(next2_vec_radians - next_vec_radians) < THRESHOLD_RADIANS:
                            p.drop(i) # `this` is an outlier
                            i += 2    # skip `next` and `next2`, both are the first points of a new curve
                        else:
                            i += 1 # go to the next point

    # Restore the original scale of the coordinates
    if p.xlogscale:
        p.points = [Point(10**point.x, point.y) for point in p.points]
    if p.ylogscale:
        p.points = [Point(point.x, 10**point.y) for point in p.points]

    for i in range(0, 1000):
        if by_y_increase_continuity(p) == 0:
            break


def by_vec_continuous_connectivity_score(
    p: Plot,
    THRESHOLD_RADIANS: float = math.pi / 4 # [rad], 30 degrees
) -> None:
    def next_continuously_connectable(
        starting_index: int,
        successor_index: int,
        direction: str, # 'left' or 'right'
    ) -> int | None:
        CONTINUE_OFFSET_LIMIT = 4

        candidates: range
        match direction:
            case 'left':
                candidates = reversed(range(
                    max(0, successor_index - CONTINUE_OFFSET_LIMIT),
                    successor_index,
                ))
            case 'right':
                candidates = range(
                    successor_index + 1,
                    min(p.size(), successor_index + 1 + CONTINUE_OFFSET_LIMIT),
                )
            case _:
                raise ValueError("direction must be 'left' or 'right''")
        starting_point, successer_point = p.get(starting_index), p.get(successor_index)
        angle = math.atan2(successer_point.y - starting_point.y, successer_point.x - starting_point.x)
        for i in candidates:
            c = p.get(i)
            c_angle = math.atan2(c.y - successer_point.y, c.x - successer_point.x)
            if abs(c_angle - angle) < THRESHOLD_RADIANS:
                return i
        else:
            return None

    by_y_increase_continuity(p)

    ##########################################################################
    # Convert scaled coordinates to linear for the outlier detection
    if p.xlogscale:
        p.points = [Point(math.log10(point.x), point.y) for point in p.points]
    if p.ylogscale:
        p.points = [Point(point.x, math.log10(point.y)) for point in p.points]
    ##########################################################################

    scores = [0] * p.size()
    for i in range(0, p.size()):
        # For each selection of initial `succ`, we get the starting vector as `start -> succ`.
        # Then, we can search, from all remaining points, the next point where
        # the angle of the vector `succ -> next` is continuous with the angle of
        # the vector starting `start -> succ`.
        # We can repeat the process by replacing `start` with `succ` and `succ` with `next`.
        # 
        # Let's say the number of points that can be continuously connected by these vectors
        # is the `max_continuously_connectable_group_size`, and define it as
        # *the score of the initial starting point with the initial successor point* .
        # 
        # For instance, when the intial successor point is a outlier, the score will be 0
        # or very low.
        # 
        # Then, by trying all possible initial successor points, we can get the maximum score
        # of the initial starting point.
        # Let's define this as the (final) *score of the initial starting point*.

        left_score = 0
        for initial_succ in reversed(range(max(0, i - 2), i)):
            score_for_this_initial_succ = 0
            start, succ = i, initial_succ
            # print(f"[left ] start, initial_succ: {start}, {initial_succ}")
            while succ is not None:
                score_for_this_initial_succ += 1
                next = next_continuously_connectable(start, succ, 'left')
                start, succ = succ, next
            # print(f"[left ] score_for_this_initial_succ: {score_for_this_initial_succ}")
            left_score = max(left_score, score_for_this_initial_succ)

        right_score = 0
        for initial_succ in range(i + 1, min(i + 1 + 2, p.size())):
            score_for_this_initial_succ = 0
            start, succ = i, initial_succ
            # print(f"[right] start, initial_succ: {start}, {initial_succ}")
            while succ is not None:
                score_for_this_initial_succ += 1
                next = next_continuously_connectable(start, succ, 'right')
                start, succ = succ, next
            # print(f"[right] score_for_this_initial_succ: {score_for_this_initial_succ}")
            right_score = max(right_score, score_for_this_initial_succ)
        
        scores[i] = left_score + right_score

        print(f"{left_score} + {right_score} = {scores[i]}")

    # Remove the outliers from the plot based on the scores.
    # The points with 0 or very small scores are considered outliers and removed.
    threshold = max(scores) / 6
    print(f"threshold: {threshold}")
    print(f"scores: {scores}")
    dropshift = 0
    for i in range(0, p.size()):
        if scores[i] < threshold:

            print(f"dropping {i} ({scores[i]})")

            p.drop(i - dropshift)
            dropshift += 1

    ##########################################################################
    # Restore the original scale of the coordinates
    if p.xlogscale:
        p.points = [Point(10**point.x, point.y) for point in p.points]
    if p.ylogscale:
        p.points = [Point(point.x, 10**point.y) for point in p.points]
    ##########################################################################

