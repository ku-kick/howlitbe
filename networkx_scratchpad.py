import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class DynamicPlotApp:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        self.root = ctk.CTk()
        self.root.geometry("1200x600")
        self.root.title("Dynamic Scatter Plot with Controls")

        # Frame for the plot
        self.frame = ctk.CTkFrame(master=self.root, fg_color="darkblue")
        self.frame.place(relx=0.33, rely=0.025, relwidth=0.66, relheight=0.95)

        # Button to update the plot
        self.button = ctk.CTkButton(master=self.root, text="Update Graph", command=self.update_plot)
        self.button.place(relx=0.025, rely=0.25,)

        # Entry for number of points
        self.input = ctk.CTkEntry(master=self.root, placeholder_text="Number of Points")
        self.input.place(relx=0.025, rely=0.5)

        # Slider for point size
        self.slider = ctk.CTkSlider(master=self.root, from_=1, to=1000, number_of_steps=999)
        self.slider.place(relx=0.025, rely=0.75)

        # Initial plot
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # Adding navigation toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.frame)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        self.update_plot()  # Initial plot

        self.root.mainloop()

    def update_plot(self):
        # Clear the previous plot
        self.ax.clear()

        # Get number of points from input
        num_points = int(self.input.get()) if self.input.get().isdigit() else 100
        sizes = self.slider.get()

        # Generate random data
        x = np.random.rand(num_points)
        y = np.random.rand(num_points)
        self.ax.scatter(x, y, s=sizes, c='blue', alpha=0.5)

        # Update the plot
        self.ax.axis("off")
        self.canvas.draw()

if __name__ == "__main__":
    app = DynamicPlotApp()
