from numpy import *

# Private functions ############################################################
def _zcd(x, rising=True):
    """Find all indexes just before a zero-crossing."""
    if rising:
        return where(0 < diff(sign(x)))[0]
    else:
        return where(0 > diff(sign(x)))[0]

def _pearson_correlation_coefficient(x, y):
    """Pearson correlation coefficient. """
    n = len(x)    
    Sy = sum(y)
    Sx = sum(x)
    
    N1 = n*sum(x*y)
    N2 = Sx * Sy
    D1 = n*sum(x*x) - Sx*Sx
    D2 = n*sum(y*y) - Sy*Sx
    if D1*D2 < 0:
        return 0
    
    r = (N1 - N2)/sqrt(D1 * D2)
    return r

def _loop_point_correlation(x, l1, l2, overlap):
    """Evaluate the correlation between the start and the stop point."""
    try:
        assert(l1-overlap//2 > 0)
        assert(l2-overlap//2 > 0)
        assert(l1+overlap//2 < len(x))
        assert(l2+overlap//2 < len(x))
    except AssertionError:
        raise IndexError
    
    x1 = x[l1-overlap//2 : l1+overlap//2]
    x2 = x[l2-overlap//2 : l2+overlap//2]
    
    if len(x1) != len(x2):
        raise IndexError("{:d} != {:d}".format(len(x1), len(x2)))
    else:
        return _pearson_correlation_coefficient(x1, x2)
        
def _find_best_stop(x, l1, overlap):
    """Find the best stop-point for a given start point."""
    L = len(x)
    z = _zcd(x, rising=True)
    R = zeros(L)
    
    # Loop through all other zero crossings and compute a correlation for each
    for l2 in z[(l1 < z) & (z < L-overlap//2)]:
        R[l2] = _loop_point_correlation(x, l1, l2, overlap)

    l2 = argmax(abs(R))
    return l2

def _find_loop_points_with_overlap(x, overlap):
    """Bisect the start position to find the optimal start
    and stop position for a given correlation overlap.
    """
    
    L = len(x)
    zero_crossings = _zcd(x, rising=True)
    nearest_zero_crossing = lambda n: zero_crossings[argmax(zero_crossings > n)]
    frac = lambda x: nearest_zero_crossing(x*L)

    p1 = nearest_zero_crossing(overlap)
    p2 = nearest_zero_crossing(L - overlap)
    
    # Use bisection to obtain the best start point
    # p = start point
    # s = stop point
    
    score1 = 0
    score2 = 0
    pbest = p1
    sbest = 0
    p1prev = None
    p2prev = None
    for n in range(200):
        # Check if too close to boundaries
        if p1 - overlap//2 < 0:
            break
        elif p2 + overlap//2 > L-1:
            break
        
        s1 = _find_best_stop(x, p1, overlap)
        s2 = _find_best_stop(x, p2, overlap)
        score1 = _loop_point_correlation(x, p1, s1, overlap)
        score2 = _loop_point_correlation(x, p2, s2, overlap)
        pcenter = nearest_zero_crossing((p1+p2)/2)
        
        if score1 < score2:
            pbest = p2
            sbest = s2
            p1 = pcenter
        else:
            pbest = p1
            sbest = s2
            p2 = pcenter

        # Check for convergence
        if p1 == p1prev and p2 == p2prev:
            break
        else:
            p1prev = p1
            p2prev = p2

    return pbest, sbest

# Public functions #############################################################
def find_loop_points(x):
    """Automatically find the optimal loop points for a given audio vector."""
    
    x = array(x, dtype=float)
    
    results = []
    Rmax = -inf
    nmax = None
    overlaps = [int(X*len(x)) for X in [0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3]]
    percent = lambda X: 100 * X/len(x)
    
    l1 = 0
    l2 = 0
    for n, overlap in enumerate(overlaps):
        try:
            l1, l2 = _find_loop_points_with_overlap(x, overlap)
            R = _loop_point_correlation(x, l1, l2, overlap)
        except IndexError:
            continue
        
        results.append([l1, l2, R])
        
        if Rmax < R:
            Rmax = R
            nmax = n

    overlap = overlaps[nmax]
    l1, l2 = results[nmax][0], results[nmax][1]
    R = _loop_point_correlation(x, l1, l2, overlap)
    return l1, l2, R
   
