"""PA-NS-001 deterministic analytical reference and independent checks; research prototype."""
import math

def reference(kind, y, h=1.0, U=1.0, mu=1.0, G=2.0):
    if h <= 0 or mu <= 0 or not all(map(math.isfinite, (y,h,U,mu,G))):
        raise ValueError('invalid physical parameters')
    if kind == 'couette': return U*y/h
    if kind == 'poiseuille': return G*y*(h-y)/(2*mu)
    raise ValueError('unknown flow')

def verify(kind, values, *, h=1.0, U=1.0, mu=1.0, G=2.0, tolerance=1e-9):
    """Validate equally spaced velocity samples; residual via second difference.

    Tolerance is illustrative, not calibrated or preregistered for a main study.
    """
    n=len(values)
    if n < 5 or h <= 0 or mu <= 0 or tolerance <= 0: raise ValueError('invalid configuration')
    if not all(math.isfinite(v) for v in values): return {'accepted':False,'reason':'nonfinite'}
    dy=h/(n-1)
    target=[reference(kind,i*dy,h,U,mu,G) for i in range(n)]
    scale=max(max(abs(x) for x in target),1.0)
    profile=max(abs(a-b) for a,b in zip(values,target))/scale
    boundary=max(abs(values[0]-target[0]),abs(values[-1]-target[-1]))/scale
    rhs=0.0 if kind=='couette' else -G/mu
    residual=max(abs((values[i+1]-2*values[i]+values[i-1])/dy**2-rhs) for i in range(1,n-1))
    residual_scale=max(abs(rhs),1.0)
    accepted=profile <= tolerance and boundary <= tolerance and residual/residual_scale <= tolerance
    return {'accepted':accepted,'profile_error':profile,'boundary_error':boundary,'momentum_residual':residual/residual_scale}
