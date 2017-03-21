#
# Batch reactor example from Biegler book on Nonlinear Programming Chapter 9
#
# Inside the reactor we have the first order reversible reactions
#
# A <=> B <=> C
#
# DAE model for the reactor system:
#
# zA' = -p1*zA + p2*zB, zA(0)=1
# zB' = p1*zA - (p2 + p3)*zB + p4*zC, zB(0)=0
# zA + zB + zC = 1

from pyomo.environ import *
from pyomo.dae import *
from pyomo.dae.simulator import Simulator

m = ConcreteModel()

m.t = ContinuousSet(bounds=(0.0,1))

m.p1 = Param(initialize=4.0)
m.p2 = Param(initialize=2.0)
m.p3 = Param(initialize=40.0)
m.p4 = Param(initialize=20.0)

m.za = Var(m.t)
m.zb = Var(m.t)
m.zc = Var(m.t)
m.dza = DerivativeVar(m.za)
m.dzb = DerivativeVar(m.zb)

# Setting the initial conditions
m.za[0.0] = 1
m.zb[0.0] = 0

def _diffeq1(m,t):
    return m.dza[t] == -m.p1*m.za[t]+m.p2*m.zb[t]
m.diffeq1 = Constraint(m.t,rule=_diffeq1)

def _diffeq2(m,t):
    return m.dzb[t] == m.p1*m.za[t]-(m.p2+m.p3)*m.zb[t]+m.p4*m.zc[t]
m.diffeq2 = Constraint(m.t,rule=_diffeq2)

def _algeq1(m,t):
    return m.za[t]+m.zb[t]+m.zc[t] == 1
m.algeq1 = Constraint(m.t,rule=_algeq1)


# Simulate the model using casadi
sim = Simulator(m, package='casadi')
tsim, profiles = sim.simulate(numpoints=100,integrator='idas')

varorder = sim.get_variable_order()
algorder = sim.get_variable_order(vartype='algebraic')

# Discretize model using Orthogonal Collocation
discretizer = TransformationFactory('dae.collocation')
discretizer.apply_to(m,nfe=10,ncp=3)

# Initialize the discretized model using the simulator profiles
sim.initialize_model()

import matplotlib.pyplot as plt

time = list(m.t)
za = [value(m.za[t]) for t in m.t]
zb = [value(m.zb[t]) for t in m.t]
zc = [value(m.zc[t]) for t in m.t]

for idx1,v in enumerate(varorder):
    plt.plot(tsim,profiles[:,idx1],label=v)

for idx2,v in enumerate(algorder):
    plt.plot(tsim,profiles[:,len(varorder)+idx2],label=v)

plt.plot(time,za,'o',label='za interp')
plt.plot(time,zb,'o',label='zb interp')
plt.plot(time,zc,'o',label='zc interp')
plt.xlabel('t')
plt.legend(loc='best')
plt.show()
