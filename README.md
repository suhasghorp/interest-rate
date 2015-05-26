# InterestRate

## Assignment 1

### Reports

* Develop a small library implementing B-splines. This library should be capable of calculating the derivatives and integrals of the basis functions. Make sure that you take a full advantage of the recursive properties of the basis functions. 

  - Please refer to python script: `Assignment1/splines.py`
  - `Spline` Class: with methods `splrep()`, `splint()`, `spldev()`, be capable of the derivatives and integrals of the basis functions.
  - Use cache in the function to take a full advantage of the recursive properties of the basis functions.

* Build a function that computes the discount factor between any two dates.

  - Please refer to python script: `Assignment1/curves.py`
  - Inside the `Curve` Class, `disc_factor()` is implemented, and both `OIS` and `LIBOR` classes will be derived from `Curve`.

* Build a function that computes the forward LIBOR rate for any settlement and underlying tenor.

  - Please refer to python script: `Assignment1/curves.py`
  - Inside the `Curve` Class, `forwards()` is implemented, and `LIBOR` Class will inheritant this method.

* Build a function that computes the (spot or forward) swap rate for any settlement and underlying tenor.

  - Please refer to python script: `Assignment1/swaps.py`
  - Inside the `Swap` Class, `SwapRates()` is to compute the swap rate for given settlement and underlying tenor.

* Use the enclosed market data sheet and the method described in class to build the instantaneous OIS and LIBOR curves.

  - Please refer to python script: `Assignment1/curves.py`
  - Inside the `LIBOR` and `OIS` classes, they both inheritant `r()` method in `Curve` base class, and this method is building the instantaneous curves.

* Build a function that calculates the PV of any spot or forward starting swap based on your curves.

  - Please refer to the main file: `Assignment1/main.py`

### Usage

* Step 1: Please make sure your computer has installed python2 and required modules, if not and you want to test this assignment by running the program, please go https://github.com/weiyialanchen/MacInstallation and follow the installation guide.

* Step 2: Download the repository by
  ``` git clone https://github.com/weiyialanchen/InterestRate.git```

* Step 3: Go to Assignment 1 directory and run the main file
  ```
  cd ~/InterestRate/Assignment1
  python main.py
  ```


## Assignment 2

### Reports

* Implement the model using Euler’s scheme (note that for the normal LMM, Euler’s and Milstein’s schemes are identical). For drift term calculations, implement the ability to do both: the exact calculation and the frozen curve approximation.

  - Please refer to python script: `Assignment2/libor_market.py`
  - The exact calculation: set the parameter `b_frozenCurve` as `False`
  - The frozen curve approximation: set the paramter `b_frozenCurve` as `True`

* Apply your model to a spot starting 10 year knock-out swap. A knock-out swap is an interest rate swap with a special termination feature. Namely, if, on a fixed leg coupon date (or more precisely, two business days before), the 10 year swap rate sets below a preset barrier B, the swap is terminated. Notice that this is a path dependent derivative and Monte Carlo simulations are an appropriate approach to pricing this product. Use 2000 simulated paths to carry out the calculation. As a variance reducing method, you may also consider using antithetic variables.

  - Knock-out swap: `Knock_Out_Swap` class in `Assignment2/swaps.py` derived from `Swap` class implemented in Assignment1
  - Monte Carlo Simulation: please refer to `Knock_Out_Swap.simulate()`

* 2000 simulated paths calculation, assuming B = 0.95%, determine the break-even rate on the fixed leg of the swap.

  - Please refer to `calc_swapRate()` in `Assignment2/main.py`, see output for 2000 paths below
  ```
  Use 2,000 simulated paths to carry out the calculation (the exact calculation) - 
  The break-even rate on the fixed leg of the swap: 	0.0222146461996 
  
  Use 2,000 simulated paths to carry out the calculation (the frozen curve approximation) - 
  The break-even rate on the fixed leg of the swap: 	0.0221701123552
  ```

* How accurate is your calculation? Compare against a run with 5,000 simulated paths.

  - Please refer to `calc_swapRate()` in `Assignment2/main.py`, see output for 5000 paths below
  ```
  Compare against a run with 5,000 simulated paths - 
  The break-even rate on the fixed leg of the swap: 	0.0227748459579
  ```
  It's very accurate, with error around `2%`.

* Analyse the performance of each of the drift terms calculation methods, and the accuracy of the frozen curve approximation.

  - The performance between different methods is very close, though the exact calculation is more accurate in theory. 
  - But the error of frozen curve approximation method is smaller than 0.01 digits / 2% error, a good enough approximation.
  
### Usage

* Step 1: Please make sure your computer has installed python2 and required modules, if not and you want to test this assignment by running the program, please go https://github.com/weiyialanchen/MacInstallation and follow the installation guide.

* Step 2: Download the repository by
  ``` git clone https://github.com/weiyialanchen/InterestRate.git```

* Step 3: Go to Assignment 2 directory and run the main file
  ```
  cd ~/InterestRate/Assignment2
  python main.py
  ```
