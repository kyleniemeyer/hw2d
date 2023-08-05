# The Hasegawa-Wakatani model of plasma turbulence

This repository contains a reference implementations for the Hasegawa-Wakatani model in two dimensions using Python.
The purpose is to provide a playground for education and scientific purposes: be it testing numerical or machine learning methods, or building related models quicker.

Stable, verified parameters will be published with this repository.

### Installation 

Install a pure NumPy version via
```pip install hw2d```
and to include accelerators like numba, use the following:
```pip install hw2d[accelerators]```

### Reference Methods

The implementation presented here is by no means meant to be the optimal, but an easy to understand starting point to build bigger things upon and serve as a reference for other work.
This reference implementation uses:
- Gradients $\left(\partial_x, \partial_y, \nabla \right)$: Central finite difference schemes (2nd order accurate)
- Poisson Bracket $\left([\cdot, \cdot]\right)$: Arakawa Scheme (2nd order accurate, higher order preserving)
- Poisson Solver $\left(\nabla^{-2}\cdot\right)$: Fourier based solver
- Time Integration $\left(\partial_t\right)$: Explicit Runge Kutte (4th order accurate)
The framework presented here can be easily extended to use alternative implementations.

### Contributions encouraged

Pull requests are strongly encouraged. 

The simplest way to contribute is running simulations and committing the results to the historical runs archive. This helps in exploring the hyper-parameter space and improving statistical reference values for all.

If you don't know where to start in contributing code, implementing new numerical methods or alternative accelerators make for good first projects!

### Code guidelines

All commits are auto-formatted using `Black` to keep a uniform presentation.


## The Hasegawa-Wakatani Model

The HW model describes drift-wave turbulence using two physical fields: the density $n$ and the potential $\phi$ using various gradients on these.

$$
\begin{align}
    \partial_t n &= c_1 \left( \phi - n \right)
                     - \left[ \phi, n \right]
                     - \kappa_n \partial_y \phi
                     - \nu \nabla^{2N} n 
             \\
    \partial_t \Omega &= c_1 \left( \phi - n \right)
                                      - \left[ \phi, \Omega \right]
                                      - \nu \nabla^{2N} \Omega 
             \\
             \Omega &= \nabla^2 \phi
\end{align}
$$


## Dynamics of the different phases

The model produces self-organizing turbulent structures in a three distinct stages: initial self-organization, linear drift waves, and a stable turbulent phase.

For the interesting intermediary phase for the adiabatic coefficient, $c_1=1$, the initial perturbation will start organizing to produce linear drift waves through the $\partial_t \phi$ component. 
The system transitions into this first linear phase at roughly t=15, saturates at around t=45, and breaks down to transition into the turbulent phase at about t=80.
The turbulent phase is visually saturated at around t=125, but physical parameters overshoot and only fall into the long term stable pahse at aroung t=200. 


## Physical Properties

### Numerical values for each frame
The reason why the Hasegawa-Wakatani Model has been the de-facto testing bed for new methods are its statistically stationary properties of the complex turbulent system.
The moduel includes all code needed to generate these values.
It goes further, however, and provides reference values with statistical bounds for the first time for a vast range of values.
This allows simple comparison, as well es evalutaion of new methods to one reference community built resource.

$$
\begin{align}
    \Gamma^n       &= -     \iint{ \mathrm{d}^2x \space \left( n \space \partial_y \phi \right) } \\
    \Gamma^c       &= c_1   \iint{ \mathrm{d}^2x \space \left(n - \phi \right)^2} \\
    E              &= \small \frac{1}{2} \normalsize \iint{\mathrm{d}^2 x \space \left(n^2 - \left|\nabla_\bot \phi \right|^2 \right)} \\
    U              &= \small \frac{1}{2} \normalsize \iint{\mathrm{d}^2 x \space \left(n-\nabla_\bot^2  \phi\right)^2} = \small \frac{1}{2} \normalsize \iint{\mathrm{d}^2 x \space \left(n-\Omega\right)^2}
\end{align}
$$


### Spectral values for each frame

Additionally, spectral properties are planned to be included, among these are:

$$
\begin{align}
  \int{\mathrm{d} k_y \space \Gamma^n \small (k_y) \normalsize }  &= - \int{\mathrm{d} k_y \left( i k_y  \space n \small (k_y) \normalsize \space \phi^* \small (k_y) \normalsize \right) } \\
  \delta \small (k_y) \normalsize &= - \mathrm{Im}\left( \mathrm{log} \left( n^* \small (k_y) \normalsize \space \phi \small (k_y) \normalsize \right) \right) \\
  E^N \small (k_y) \normalsize &= \small \frac{1}{2}\normalsize \big| n \small (k_y) \normalsize \big|^2 \\
  E^V \small (k_y) \normalsize &= \small \frac{1}{2}\normalsize \big| k_y \space \phi \small (k_y) \normalsize \big|^2 
\end{align}
$$


### Predictable in- and outflows over time

Finally, due to the definition of the fields as perturbation fields with background desnity gradients, the system gains and loses energy and enstrophy in a predictable manner.
The conservation of these are also tested within the continuous integration pipeline.

$$
\begin{align}
    \partial_t E   &= \Gamma^N - \Gamma ^c - \mathfrak{D}^E  \\
    \partial_t U   &= \Gamma^N - \mathfrak{D}^U  \\ 
    \mathfrak{D}^E &= \quad \iint{ \mathrm{d}^2x \space (n \mathfrak{D^n} - \phi \mathfrak{D}^\phi)} \\ 
    \mathfrak{D}^U &= -     \iint{ \mathrm{d}^2x \space (n - \Omega)(\mathfrak{D}^n - \mathfrak{D}^\phi)} \\
    with \quad \mathfrak{D}^n \small (x,y) \normalsize &= \nu \nabla^{2N} n \quad and \quad 
    \mathfrak{D}^\phi \small (x,y) \normalsize = \nu \nabla^{2N} \phi  
\end{align}
$$

### General notes

It is the common practice across all reference texts to calculate $\int\cdot$ as $\langle \cdot \rangle$ for a unitless box of size one in order to get comparable values for all properties.


## Common Issues in Simulating HW2D

### Crashing/NaN encountered 

#### within < 10 timesteps

The simulation has exploded in one direction. Most commonly this means that the hyper-diffusion components are too large. 
- reduce the hyper diffusion order: `N`
- reduce the diffusion coefficient: `nu`
- reduce the initial perturbation: `scale`


#### around t=75-125

The timestep is too big in the turbulent phase. CFL criteria are no longer satisfied and simulation crashes.
- reduce: `step_size`

### Chessboard pattern emerges

The energy accumulates at grid scale. Hyper-diffusion component is not large enough to dissipate the energy.
- increase: `nu`
- increase: `N`
  

### Physical values deviate from references

The HW2D model can create stable simulations that are underresolved, through very large hyper-diffusion terms. A higher resolution is needed for this box size.
- increase: `grid_pts`
