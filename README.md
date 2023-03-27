# Overview

Framework for learning Behavior Trees (BTs) based on Genetic Programming (refer to [this paper](https://ieeexplore.ieee.org/abstract/document/9562088/)) and Learning from Demonstration (refer to [this paper](https://ieeexplore.ieee.org/abstract/document/9562088)).  
The target tasks are robotic manipulation ones and are simulated in the AGX Dynamics from Algopryx.

## Experiments

* The [GUI](./simulation/simulation/algoryx/combined/gui.py) allows user to add demonstrations and start/stop/resume the evolution of BTs through the genetic programming.
* The experiments are defined by uncommenting the corresopnding lines in the [config file](./simulation/simulation/algoryx/config/gp_targets.yaml). Morover, adjust the [parameters](./simulation/simulation/algoryx/config/sim_data.yaml) as explained in the paper.
* For all experiments but the last, set [`random_bringup`](./simulation/simulation/algoryx/config/sim_data.yaml#L32) to `False`.
* The data with which the plots for the paper have been obtained are provided in the [log folder](./simulation/simulation/algoryx/logs).


## Disclaimer
To run the experiment is necessary to have a valid license and installation of the simulator from Algoryx. Please contact the authors of the paper for further instructions.


---

### Note on test routines for Copyright

The LICENSE notice is of type `BSD-3-Clause License`, that doesn't seem to be automatically recognised by the `test_copyright.py` script.  
To ignore looking for the LICENSE notice, it is necessary to modify the `main` function in the source code of the test routine, located in `/opt/ros/foxy/lib/python3.8/site-packages/ament_copyright/main.py` (Ubuntu) or in `C:\opt\ros\foxy\x64\Lib\site-packages\ament_copyright\main.py` (Windows). To do so, comment out the lines from `157` to `161` and substitute them with this block, which just removes the LICENSE check:
```python
else:
    message = 'copyright=%s' % \
        (', '.join([str(c) for c in file_descriptor.copyrights]))
    has_error = False
```
