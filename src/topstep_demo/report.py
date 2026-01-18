from rich.console import Console
from rich.table import Table
from typing import List, Tuple
from .broker import Trade

def generate_report(trades: List[Trade], final_cash: float, initial_cash: float, equity_curve: List[float]):
    """
    Generate a professional performance report.
    """
    console = Console()
    
    # metrics
    total_trades = len(trades)
    realized_pnl = sum([t.realized_pnl for t in trades if t.realized_pnl is not None])
    
    # Calculate Drawdown
    peak = -float('inf')
    max_drawdown = 0.0
    for e in equity_curve:
        if e > peak:
            peak = e
        dd = (peak - e) / peak if peak > 0 else 0
        if dd > max_drawdown:
            max_drawdown = dd
            
    # Wins/Losses
    wins = len([t for t in trades if t.realized_pnl and t.realized_pnl > 0])
    losses = len([t for t in trades if t.realized_pnl and t.realized_pnl <= 0])
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0.0

    table = Table(title="Backtest Performance Report", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Trades", str(total_trades))
    table.add_row("Win Rate", f"{win_rate:.1f}% ({wins} W / {losses} L)")
    table.add_row("Realized PnL", f"${realized_pnl:,.2f}")
    table.add_row("Final Equity", f"${equity_curve[-1]:,.2f}" if equity_curve else "N/A")
    table.add_row("Max Drawdown", f"{max_drawdown*100:.2f}%")
    table.add_row("Initial Cash", f"${initial_cash:,.2f}")
    
    console.print(table)
    
    if total_trades > 0:
        t_table = Table(title="Use 'topstep-demo --log-level DEBUG' to see full trade list", show_header=True)
        t_table.add_column("Time", style="dim")
        t_table.add_column("Side")
        t_table.add_column("Price")
        t_table.add_column("PnL")
        
        # Show last 5
        for t in trades[-5:]:
            pnl_s = f"${t.realized_pnl:.2f}" if t.realized_pnl is not None else "-"
            s_style = "green" if t.side == "BUY" else "red"
            t_table.add_row(str(t.timestamp), f"[{s_style}]{t.side}[/{s_style}]", f"{t.price:.2f}", pnl_s)
        console.print(t_table)
