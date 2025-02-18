import matplotlib.pyplot as plt
import streamlit as st

def plot_data_per_signal(data_points_dict):
    """Plots signal data."""
    for signal_name, data_points in data_points_dict.items():
        x_values, y_values = zip(*data_points)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(x_values, y_values, label=signal_name, linewidth=1.5)
        ax.set_title(f"Graph for Signal: {signal_name}")
        ax.set_xlabel("Time")
        ax.set_ylabel("Value")
        ax.legend()
        ax.grid()
        st.pyplot(fig)
        plt.close(fig)

