# Setup
1. Download the .zip, or clone the repo.
2. Extract if necessary, and `cd` to the root directory (the one with this file in it)
2. [Download](https://conda.io/miniconda.html) and install Miniconda, or Anaconda if you prefer. Using a Conda distribution is the easiest way (that I know of) to set up the required Python environment and packages.
3. Now, create the Python 3.4 virtual environment which Robovis will run in:

    `conda create -n <NAME> python=3.4 numpy=1.11 pyqt=5.6`

    Replace \<NAME\> with whatever name you like for the environment - 'py34' is what I use.

4. Activate the environment; on Windows:

    `activate <NAME>`

    Or, on UNIX:

    `source activate <NAME>`

5. Install remaining packages:

    ```
    pip install PyYAML
    conda install -c menpo opencv3
    ```

You should then be able to run Robovis from the root directory with `python .`
