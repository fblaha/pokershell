# PokerShell

[![Build Status](https://api.travis-ci.org/fblaha/pokershell.svg?branch=master)](https://api.travis-ci.org/fblaha/pokershell)
[![PyPI version](https://img.shields.io/pypi/v/pokershell.svg)](https://pypi.python.org/pypi/pokershell)
[![PyPI downloads](https://img.shields.io/pypi/dm/pokershell.svg)](https://pypi.python.org/pypi/pokershell)

Texas hold 'em command line calculator and simulator. Handy tool for online poker players. Easy to use CLI interface
provides handful information about possible game outcomes:
* win/tie/lose probability for the player
* statistics of winning hands - provides statistics of possible winning hands
* statistics of beating hands - provides statistics of possible opponent's hands
* covers all betting rounds/streets

## Example
```
(pokershell) jdqs 5 0.08;  5h6c5s 3 0.62; 7h 1.02

Game :
+-------+----------+------+------------+----------+--------------+------+------------+
|  Hole |   Flop   | Turn | Player Num |   Hand   |    Ranks     | Pot  | Pot Growth |
+-------+----------+------+------------+----------+--------------+------+------------+
| J♦ Q♠ |    -     |  -   |     5      |    -     |      -       | 0.08 |     -      |
| J♦ Q♠ | 5♥ 6♣ 5♠ |  -   |   3(-2)    | ONE_PAIR | (5, Q, J, 6) | 0.62 |    675%    |
| J♦ Q♠ | 5♥ 6♣ 5♠ |  7♥  |     3      | ONE_PAIR | (5, Q, J, 7) | 1.02 |    65%     |
+-------+----------+------+------------+----------+--------------+------+------------+

Simulation (monte-carlo):
+---------------+-------------+----------------+--------+--------+
|      Win      |     Tie     |      Loss      | Equity | Leader |
+---------------+-------------+----------------+--------+--------+
| 12.96% (3151) | 1.09% (265) | 85.95% (20891) |  0.13  |   no   |
+---------------+-------------+----------------+--------+--------+
+---------------+----------+--------------+-----------+
|  Winning Hand | Win Freq | Beating Hand | Beat Freq |
+---------------+----------+--------------+-----------+
|    TWO_PAIR   |  70.93%  |   TWO_PAIR   |   45.24%  |
|    ONE_PAIR   |  25.61%  |   ONE_PAIR   |   17.04%  |
| THREE_OF_KIND |  3.46%   |   STRAIGHT   |   16.61%  |
+---------------+----------+--------------+-----------+

Simulation finished in 1.03 seconds

(pokershell)
```
## Installation

* [install Python 3.4 or 3.5](https://www.python.org/downloads/).
* clone this repository via git client or use "Download ZIP" link to download this repository
* go to root directory of downloaded repository
* launch setup script `python setup.py install`
* launch pokershell `pokershell` (use `-h` to display help)
