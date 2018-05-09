# cs410finalproject

## Getting Started

### Installing Requirements

Run the following command in terminal to install the required libraries

```
pip3 install -r requirements.txt
```

## Usage

There are three main ways to use this application: 

* Direct input 
* File input
* Twitter Data

In each case, navigate to the forked folder to use the application.

### Direct Input

Run a command such as this to normalize direct user input.

```
main.py ‘Aaron likes dirty old foood, 4eva'
```

### File Input

Run a command such as this to normalize data from a file. Note: Each line in the input file must be a phrase or collection of text you wish to normalize. The input file must adhere to this format exactly.

```
main.py ‘file’ ‘file.txt'
```

### Twitter Data

The final usage option is to supply a keyword to parse twitter data for normalization. Run a command such as this.

```
main.py ‘tweets’ ‘4eva'
```

