# general imports
import warnings

# numpy
import numpy as np
from numpy.random import rand
from numpy.random import randn
import numpy.linalg as la

# rcognita
from . import utilities

class EndiSystem(utilities.Generic):
    """
    Class denoting the RL environment.

    ----------
    Parameters
    ----------

    dim_state : int
        dimension of state vector
        x_t = [x_c, y_c, alpha, upsilon, omega]
    
    dim_input : int
        * dimension of action vector
        * u_t = [F, M]
    
    dim_output : int
        * dimension of output vector
        * x_t+1 = [x_c, y_c, alpha, upsilon, omega]
    
    dim_disturb : int
        * dimension of disturbance vector
        * actuator disturbance that gets added to F and M
    
    initial_x : int
        * initial x coordinate of robot
    
    initial_y : int
        * initial x coordinate of robot
    
    m : int
        * m = robot's mass
    
    I : int
        * I = moment of inertia about the vertical axis
    
    f_min, f_max, m_min, m_max : all int
        * control bounds
    
    f_man : int
        * manual control variable for pushing force
    
    m_man: int
        * manual control variable for steering/turning torque
    
    is_dyn_ctrl : int
        * is dynamic control?
        * If 1, the controller (a.k.a. agent) is considered as a part of the full state vector
    

    is_disturb : int
        * use disturbance?
        * If 0, no disturbance is fed into the system
    
    sigma_q, mu_q, tau_q : int
        * hyperparameters to disturbance
    
    ----------
    Attributes
    ----------
    
    alpha : float
        * turning angle
    
    system_state
        * state of the environment
        * can be a vector or matrix (if there are multiple sub-states, i.e. for multiple controllers)
    
    _dim_initial_full_state : int vector
        * dimensions of full state
    
    full_state : int vector
        * includes the system state vector, control input vector and disturbance vector
        * can be a vector or matrix (if there are multiple sub-states, i.e. for multiple controllers)
    
    u0 : float vector
        * control input vector
    
    q0 : float vector
        * disturbance vector
    
    num_controllers : int
        * number of controllers to be used with the environment
    
    multi_sim : int
        * used with multiple controllers (num_controllers > 1)
        * variable used for the closed_loop function
        * specifies that the closed_loop is being executed for a specific controller
    
    ---------------------
    Environment variables
    ---------------------
    
    x_с : x-coordinate [m]
    
    y_с : y-coordinate [m]
    
    alpha : turning angle [rad]
    
    v : speed [m/s]
    
    omega : revolution speed [rad/s]
    
    F : pushing force [N]
    
    M : steering torque [Nm]
    
    m : robot mass [kg]
    
    I : robot moment of inertia around vertical axis [kg m^2]
    
    q  : actuator disturbance
    """

    def __init__(self,
                 dim_state=5,
                 dim_input=2,
                 dim_output=5,
                 dim_disturb=2,
                 initial_x=5,
                 initial_y=5,
                 m=10,
                 I=1,
                 f_man=-3,
                 m_man=-1,
                 f_min=-5,
                 f_max=5,
                 m_min=-1,
                 m_max=1,
                 is_dyn_ctrl=0,
                 is_disturb=0,
                 sigma_q=None,
                 mu_q=None,
                 tau_q=None):

        self.dim_state = dim_state
        self.dim_input = dim_input
        self.dim_output = dim_output
        self.dim_disturb = dim_disturb

        if is_dyn_ctrl:
            self._dim_initial_full_state = self.dim_state + self.dim_disturb + self.dim_input
        else:
            self._dim_initial_full_state = self.dim_state + self.dim_disturb

        self.m = m
        self.I = I
        self.f_min = f_min
        self.f_max = f_max
        self.m_min = m_min
        self.m_max = m_max
        self.f_man = f_man
        self.m_man = m_man
        self.u_man = np.array([f_man, m_man])
        self.control_bounds = np.array([[f_min, f_max], [m_min, m_max]])
        self.initial_x = initial_x
        self.initial_y = initial_y
        self.num_controllers = 1
        self.q0 = np.zeros(dim_disturb)
        self.u0 = np.zeros(dim_input)
        self.is_dyn_ctrl = is_dyn_ctrl
        self.multi_sim = None

        # initial values of the system's state
        self.initial_alpha = self.alpha = initial_alpha = np.pi / 2
        initial_state = np.zeros(dim_state)
        initial_state[0] = initial_x
        initial_state[1] = initial_y
        initial_state[2] = initial_alpha
        self.system_state = initial_state

        self.full_state = self.create_full_state(
            self.system_state, self.q0, self.u0, is_dyn_ctrl)

        """ disturbance """
        self.is_disturb = is_disturb
        self.sigma_q = sigma_q
        self.mu_q = mu_q
        self.tau_q = tau_q

    def create_full_state(self, system_state, u0, q0=None, is_dyn_ctrl=0):
        if is_dyn_ctrl:
            self.full_state = np.concatenate([self.system_state, u0, q0])
        else:
            self.full_state = np.concatenate([self.system_state, u0])

        return self.full_state

    def add_bots(self, initial_x, initial_y, number=1):
        self.new_state = np.zeros(self.dim_state)
        self.new_state[0] = initial_x
        self.new_state[1] = initial_y
        self.new_state[2] = self.initial_alpha

        self.system_state = np.vstack((self.system_state, self.new_state))

        if self.u0.ndim == 1:
            self.u0 = np.tile(self.u0, (2, 1))

        elif self.u0.ndim > 1:
            new_row = self.u0[0, :]
            self.u0 = np.vstack((self.u0, new_row))

        if self.q0.ndim == 1:
            self.q0 = np.tile(self.q0, (2, 1))

        elif self.q0.ndim > 1:
            new_row = self.u0[0, :]
            self.q0 = np.vstack((self.q0, new_row))

        if self.is_dyn_ctrl:
            self.full_state = np.concatenate(
                (self.system_state, self.q0, self.u0), axis=1)
        else:
            self.full_state = np.concatenate(
                (self.system_state, self.q0), axis=1)

        self.alpha = self.system_state[:, 2]

        self.num_controllers += 1

    @staticmethod
    def _get_system_dynamics(t, x, u, q, m, I, dim_state, is_disturb):
        """ Get internal system dynamics
            Generalized derivative of: x_t+1 = f(x_t, u_t, q_t)
        
        where:
            x -- state
            u -- input
            q -- disturbance
        References
        
        ----------
        .. [1] W. Abbasi, F. urRehman, and I. Shah. “Backstepping based nonlinear adaptive control for the extended
            nonholonomic double integrator”. In: Kybernetika 53.4 (2017), pp. 578–594
        """
        
        system_dynamics = np.zeros(dim_state)

        F = u[0]
        M = u[1]
        alpha = x[2]
        v = x[3]
        omega = x[4]

        # compute new values
        D_x = v * np.cos(alpha)
        D_y = v * np.sin(alpha)
        D_alpha = omega
        D_v = F / m
        D_omega = M / I

        # assign next state dynamics
        system_dynamics[0] = D_x
        system_dynamics[1] = D_y
        system_dynamics[2] = D_alpha
        system_dynamics[3] = D_v
        system_dynamics[4] = D_omega

        return system_dynamics

    @staticmethod
    def get_curr_state(x, u=[]):
        """ Return current state of system """
        y = x
        return y

    def _add_disturbance(self, t, q):
        """ Dynamical disturbance model """

        Dq = np.zeros(self.dim_disturb)

        if self.is_disturb:
            for k in range(0, self.dim_disturb):
                Dq[k] = - tau_q[k] * (q[k] + sigma_q[k] * (randn() + mu_q[k]))

        return Dq

    def _create_dyn_controller(t, u, y):
        """
        Dynamical controller.
        
        When `is_dyn_ctrl=0`, the controller is considered static, which is to say that the control actions are computed immediately from the system's output.
        In case of a dynamical controller, the system's state vector effectively gets extended.
        
        Dynamical controllers have some advantages compared to the static ones. Currently, left for future implementation
        """

        Du = np.zeros(self.dim_input)

        return Du

    def set_latest_action(self, u, mid=None):
        if self.num_controllers > 1:
            self.u0[mid] = u
        else:
            self.u0 = u

    def set_multi_sim(self, mid):
        self.multi_sim = mid

    def closed_loop(self, t, full_state):
        """ Closed loop of the system.
        
        This function is designed for use with ODE solvers. Normally, you shouldn't change it
        
        Examples
        --------
        
        Assuming `sys` is a `system`-object, `t0, t1` - start and stop times, and `full_state` - a properly defined initial condition:
        >>> import scipy as sp
        >>> simulator = sp.integrate.RK45(sys.closed_loop, t0, full_state, t1)
        >>> while t < t1:
                simulator.step()
                t = simulator.t
                full_state = simulator.y
                x = full_state[0:sys.dim_state]
                y = sys.get_curr_state(x)
                u = myController(y)
                sys.set_latest_action(u)
        """

        # environment + disturbance
        if self.multi_sim is not None:
            mid = self.multi_sim

        new_full_state = np.zeros(self._dim_initial_full_state)

        x = full_state[0:self.dim_state]
        q = full_state[self.dim_state:]

        if self.is_dyn_ctrl:
            u = full_state[-self.dim_input:]
            new_full_state[-self.dim_input:] = self._create_dyn_controller(t, u, y)
        else:
            # Fetch the control action stored in the system
            if self.multi_sim is not None:
                u = self.u0[mid]
            else:
                u = self.u0

        if self.control_bounds.any():
            for k in range(self.dim_input):
                u[k] = np.clip(u[k], self.control_bounds[k, 0],
                               self.control_bounds[k, 1])

        new_full_state[0:self.dim_state] = self._get_system_dynamics(
            t, x, u, q, self.m, self.I, self.dim_state, self.is_disturb)

        if self.is_disturb:
            new_full_state[self.dim_state:] = self._add_disturbance(t, q)

        if self.multi_sim is not None:
            self.system_state[mid, :] = x
        else:
            self.system_state = x

        return new_full_state