# Topstep Trading Bot Demo

A minimal, production-style algorithmic trading bot demo designed to verify architectural readiness for a Topstep-compliant implementation. This project simulates a trading environment with a mock broker, enforcing strict risk management rules logic suitable for funding evaluations.

## Features

- **Strategy-Based Execution**:
  - Default: **Moving Average Crossover** (configurable windows).
  - Modular interface for easy extension.
- **Topstep-Style Risk Management**:
  - **One Position at a Time**: Strict limits on concurrent positions.
  - **Stop Loss & Take Profit**: Automated exit logic per trade.
  - **Long-Only Default**: Short selling disabled by default to prevent accidental risk (configurable).
- **Mock Broker**: Simulates order execution, fill tracking, and Realized PnL calculation.
- **Backtest Engine**: Dedicated high-speed backtest mode with equity curve tracking and professional reporting.
- **Structured Logging**: Professional JSON-based logs for observability.

## Architecture

```text
src/topstep_demo/
├── __init__.py
├── broker.py        # MockBroker Protocol & Implementation
├── cli.py           # Command-line interface
├── config.py        # Configuration dataclasses
├── data.py          # Price feed loader
├── report.py        # Performance Reporting (Rich Tables)
├── risk.py          # Position & Risk management (SL/TP)
├── runner.py        # Main simulation/backtest loop
├── strategy.py      # MA Crossover Strategy
└── logging_utils.py # Logging configuration
```

## Quickstart

### Prerequisites

- Python 3.10+
- `pip`

### Installation

1.  Clone the repository and enter the directory.
2.  Install the package:
    ```bash
    pip install .
    ```

### Running the Demo

#### Backtest Mode (Fast)

Run a high-speed backtest on the sample data with default parameters:

```bash
topstep-demo --mode backtest
```

**Output Example:**
```text
      Backtest Performance Report      
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Metric         ┃ Value              ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ Total Trades   │ 15                 │
│ Win Rate       │ 60.0% (9 W / 6 L)  │
│ Realized PnL   │ $1,250.00          │
│ Final Equity   │ $101,250.00        │
└────────────────┴────────────────────┘
```

#### Simulation Mode (Real-time feel)

Run with delays to simulate live trading tick-processing:

```bash
topstep-demo --mode sim
```

### Configuration Examples

**Custom MA Windows & stricter Risk:**
```bash
topstep-demo --mode backtest --fast-ma 5 --slow-ma 15 --sl-pct 0.005 --tp-pct 0.01
```

**Allowing Short Selling:**
```bash
topstep-demo --mode backtest --allow-short
```

## Extensions

- **Real Broker**: Implement the `Broker` protocol in `src/topstep_demo/broker.py` to wrap an API like Interactive Brokers or Rithmic.
- **New Strategies**: Subclass `Strategy` and implement `on_price`.

## Disclaimer

**EDUCATIONAL AND DEMO PURPOSES ONLY.**
This software is a simulation and does not interact with real financial markets. It is provided "as is" without warranty of any kind.
