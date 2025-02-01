# Import necessary libraries
import cv2  # OpenCV for image processing
import tkinter as tk  # Tkinter for GUI
from tkinter import filedialog, Scale, messagebox  # Tkinter modules for file dialogs, sliders, and message boxes
from PIL import Image, ImageTk  # PIL for image manipulation and display

# Define the main application class
class ImageProcessingApp:
    def __init__(self, root):
        # Initialize the application with the root window
        self.root = root
        self.root.title("Image Processing App")  # Set the title of the window
        self.configure_window()  # Configure the window size and position
        self.image = None  # Variable to store the original image
        self.cropped_image = None  # Variable to store the cropped image
        self.original_cropped = None  # Variable to store the original cropped image before resizing
        self.undo_stack = []  # Stack to store states for undo functionality
        self.redo_stack = []  # Stack to store states for redo functionality
        self.cropping = False  # Flag to indicate if cropping is in progress
        self.start_x, self.start_y, self.end_x, self.end_y = None, None, None, None  # Coordinates for cropping

        self.create_ui_elements()  # Create UI elements like buttons and canvases
        self.bind_shortcuts()  # Bind keyboard shortcuts to functions
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # Handle window closing event

    def configure_window(self):
        # Configure the window size and position
        screen_width = self.root.winfo_screenwidth()  # Get the screen width
        screen_height = self.root.winfo_screenheight()  # Get the screen height
        window_width = int(screen_width * 0.8)  # Set window width to 80% of screen width
        window_height = int(screen_height * 0.8)  # Set window height to 80% of screen height
        x = (screen_width - window_width) // 2  # Calculate x position to center the window
        y = (screen_height - window_height) // 2  # Calculate y position to center the window
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")  # Set window geometry
        self.root.configure(bg="lightblue")  # Set background color of the window

    def create_ui_elements(self):
        # Create and arrange UI elements
        self.top_frame = tk.Frame(self.root, bg="lightblue")  # Create a top frame for buttons
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)  # Pack the top frame

        self.image_frame = tk.Frame(self.root, bg="lightblue")  # Create a frame for the original image
        self.image_frame.pack(side=tk.LEFT, padx=10, pady=10, expand=True, fill=tk.BOTH)  # Pack the image frame
        self.cropped_frame = tk.Frame(self.root, bg="lightblue")  # Create a frame for the cropped image
        self.cropped_frame.pack(side=tk.LEFT, padx=10, pady=10, expand=True, fill=tk.BOTH)  # Pack the cropped frame
        self.control_frame = tk.Frame(self.root, bg="lightblue")  # Create a frame for control buttons
        self.control_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)  # Pack the control frame

        # Create canvases for displaying images
        self.canvas = tk.Canvas(self.image_frame, width=400, height=400, bg="gray", highlightthickness=0)
        self.canvas.pack(pady=10, expand=True, anchor=tk.CENTER)  # Pack the canvas for the original image
        self.cropped_canvas = tk.Canvas(self.cropped_frame, width=400, height=400, bg="gray", highlightthickness=0)
        self.cropped_canvas.pack(pady=10, expand=True, anchor=tk.CENTER)  # Pack the canvas for the cropped image

        # Define button style
        button_style = {"bg": "blue", "fg": "white", "padx": 10, "pady": 5}

        # Configure grid columns in the top frame
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(1, weight=1)
        self.top_frame.grid_columnconfigure(2, weight=1)
        self.top_frame.grid_columnconfigure(3, weight=1)
        self.top_frame.grid_columnconfigure(4, weight=1)
        self.top_frame.grid_columnconfigure(5, weight=1)
        self.top_frame.grid_columnconfigure(6, weight=1)

        # Create and place buttons in the top frame
        self.load_button = tk.Button(self.top_frame, text="Load Image", command=self.load_image, **button_style)
        self.load_button.grid(row=0, column=0, padx=5, sticky="ew")  # Load image button

        self.crop_button = tk.Button(self.top_frame, text="Crop", command=self.start_crop, **button_style)
        self.crop_button.grid(row=0, column=1, padx=5, sticky="ew")  # Crop button

        self.grayscale_button = tk.Button(self.top_frame, text="Grayscale", command=self.convert_to_grayscale, **button_style)
        self.grayscale_button.grid(row=0, column=2, padx=5, sticky="ew")  # Grayscale button

        self.rotate_button = tk.Button(self.top_frame, text="Rotate 90°", command=self.rotate_image, **button_style)
        self.rotate_button.grid(row=0, column=3, padx=5, sticky="ew")  # Rotate button

        self.save_button = tk.Button(self.top_frame, text="Save", command=self.save_image, **button_style)
        self.save_button.grid(row=0, column=4, padx=5, sticky="ew")  # Save button

        self.undo_button = tk.Button(self.top_frame, text="Undo", command=self.undo, **button_style)
        self.undo_button.grid(row=0, column=5, padx=5, sticky="ew")  # Undo button

        self.redo_button = tk.Button(self.top_frame, text="Redo", command=self.redo, **button_style)
        self.redo_button.grid(row=0, column=6, padx=5, sticky="ew")  # Redo button

        # Create a slider for resizing the image
        self.resize_slider = Scale(self.top_frame, from_=10, to=200, orient=tk.HORIZONTAL, label="Resize (%)", command=self.resize_image, bg="lightblue", fg="blue")
        self.resize_slider.grid(row=1, column=0, columnspan=7, padx=5, pady=10, sticky="ew")  # Place the slider

        # Bind mouse events to the canvas
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)  # Bind mouse button press event
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)  # Bind mouse drag event
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)  # Bind mouse button release event
        self.root.bind("<Configure>", self.on_window_resize)  # Bind window resize event

    def bind_shortcuts(self):
        # Bind keyboard shortcuts to functions
        self.root.bind("<Control-z>", lambda event: self.undo())  # Ctrl+Z for undo
        self.root.bind("<Control-y>", lambda event: self.redo())  # Ctrl+Y for redo
        self.root.bind("<Control-s>", lambda event: self.save_image())  # Ctrl+S for save
        self.root.bind("<Control-o>", lambda event: self.load_image())  # Ctrl+O for load
        self.root.bind("<Control-g>", lambda event: self.convert_to_grayscale())  # Ctrl+G for grayscale
        self.root.bind("<Control-r>", lambda event: self.rotate_image())  # Ctrl+R for rotate

    def load_image(self):
        # Load an image from the file system
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])  # Open file dialog
        if file_path:
            self.image = cv2.imread(file_path)  # Read the image using OpenCV
            if self.image is not None:
                self.display_image(self.image, self.canvas)  # Display the image on the canvas
                self.display_image(None, self.cropped_canvas)  # Clear the cropped canvas
                self.undo_stack.append({"original_image": self.image.copy()})  # Save the original image to the undo stack
                self.redo_stack.clear()  # Clear the redo stack
            else:
                messagebox.showerror("Error", "Failed to load image.")  # Show error if image loading fails

    def display_image(self, image, canvas):
        # Display an image on a given canvas
        if image is not None:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert image from BGR to RGB
            pil_image = Image.fromarray(image)  # Convert the image to a PIL image

            canvas_width = canvas.winfo_width()  # Get the width of the canvas
            canvas_height = canvas.winfo_height()  # Get the height of the canvas
            if canvas_width == 0 or canvas_height == 0:
                return  # Return if canvas dimensions are zero

            img_width, img_height = pil_image.size  # Get the dimensions of the image
            ratio = min(canvas_width / img_width, canvas_height / img_height)  # Calculate the scaling ratio
            new_width = int(img_width * ratio)  # Calculate the new width
            new_height = int(img_height * ratio)  # Calculate the new height
            resized_image = pil_image.resize((new_width, new_height), Image.LANCZOS)  # Resize the image
            image_tk = ImageTk.PhotoImage(resized_image)  # Convert the resized image to a Tkinter-compatible format
            canvas.image = image_tk  # Store the image reference to prevent garbage collection

            x_offset = (canvas_width - new_width) // 2  # Calculate the x offset to center the image
            y_offset = (canvas_height - new_height) // 2  # Calculate the y offset to center the image

            canvas.delete("image")  # Clear any existing image on the canvas
            canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=image_tk, tags=("image",))  # Display the image

            canvas.config(width=canvas_width, height=canvas_height)  # Update the canvas dimensions

        else:
            canvas.delete("all")  # Clear the canvas if no image is provided
            canvas.image = None  # Remove the image reference
            canvas.config(width=400, height=400)  # Reset the canvas size

    def start_crop(self):
        # Start the cropping process
        if self.image is not None:
            self.cropping = True  # Set the cropping flag to True
            messagebox.showinfo("Crop Mode", "Draw a rectangle to crop the image on the ORIGINAL image.")  # Show instructions
        else:
            messagebox.showwarning("Warning", "Please load an image first.")  # Show warning if no image is loaded

    def on_button_press(self, event):
        # Handle mouse button press event
        if self.cropping and event.widget == self.canvas:
            self.start_x, self.start_y = event.x, event.y  # Store the starting coordinates of the crop rectangle

    def on_mouse_drag(self, event):
        # Handle mouse drag event
        if self.cropping and event.widget == self.canvas:
            self.canvas.delete("rect")  # Clear any existing rectangle
            self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="red", tag="rect")  # Draw the crop rectangle

    def on_button_release(self, event):
        # Handle mouse button release event
        if self.cropping and event.widget == self.canvas:
            self.end_x, self.end_y = event.x, event.y  # Store the ending coordinates of the crop rectangle
            self.crop_image()  # Perform the crop operation
            self.cropping = False  # Reset the cropping flag

    def crop_image(self):
        # Crop the image based on the selected rectangle
        if self.image is not None:
            canvas_width = self.canvas.winfo_width()  # Get the canvas width
            canvas_height = self.canvas.winfo_height()  # Get the canvas height
            img_width, img_height = self.image.shape[1], self.image.shape[0]  # Get the image dimensions

            ratio_x = img_width / canvas_width  # Calculate the x ratio
            ratio_y = img_height / canvas_height  # Calculate the y ratio

            x1 = int(self.start_x * ratio_x)  # Calculate the x1 coordinate in the image
            y1 = int(self.start_y * ratio_y)  # Calculate the y1 coordinate in the image
            x2 = int(self.end_x * ratio_x)  # Calculate the x2 coordinate in the image
            y2 = int(self.end_y * ratio_y)  # Calculate the y2 coordinate in the image

            x1 = max(0, min(x1, img_width - 1))  # Ensure x1 is within the image bounds
            y1 = max(0, min(y1, img_height - 1))  # Ensure y1 is within the image bounds
            x2 = max(0, min(x2, img_width - 1))  # Ensure x2 is within the image bounds
            y2 = max(0, min(y2, img_height - 1))  # Ensure y2 is within the image bounds

            if x1 >= x2 or y1 >= y2:
                messagebox.showwarning("Warning", "Invalid cropping area. Please try again.")  # Show warning if the cropping area is invalid
                return

            self.cropped_image = self.image[y1:y2, x1:x2]  # Crop the image
            self.original_cropped = self.cropped_image.copy()  # Store the original cropped image
            self.display_image(self.cropped_image, self.cropped_canvas)  # Display the cropped image
            self.undo_stack.append({"original_image": self.image.copy(), "cropped_image": self.cropped_image.copy(), "original_cropped": self.original_cropped.copy()})  # Save the state to the undo stack
            self.redo_stack.clear()  # Clear the redo stack

    def resize_image(self, value):
        # Resize the cropped image based on the slider value
        if self.original_cropped is not None:
            scale = int(value) / 100  # Convert the slider value to a scale factor
            original_height, original_width = self.original_cropped.shape[:2]  # Get the original dimensions

            new_width = int(original_width * scale)  # Calculate the new width
            new_height = int(original_height * scale)  # Calculate the new height

            resized_image = cv2.resize(self.original_cropped, (new_width, new_height), interpolation=cv2.INTER_AREA)  # Resize the image
            self.cropped_image = resized_image  # Update the cropped image
            self.display_image(resized_image, self.cropped_canvas)  # Display the resized image
            self.undo_stack.append({"original_image": self.image.copy(), "cropped_image": self.cropped_image.copy(), "original_cropped": self.original_cropped.copy()})  # Save the state to the undo stack
            self.redo_stack.clear()  # Clear the redo stack

    def convert_to_grayscale(self):
        # Convert the cropped image to grayscale
        if self.cropped_image is not None:
            self.cropped_image = cv2.cvtColor(self.cropped_image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
            self.cropped_image = cv2.cvtColor(self.cropped_image, cv2.COLOR_GRAY2BGR)  # Convert back to BGR for display
            self.display_image(self.cropped_image, self.cropped_canvas)  # Display the grayscale image
            self.undo_stack.append({"original_image": self.image.copy(), "cropped_image": self.cropped_image.copy(), "original_cropped": self.original_cropped.copy()})  # Save the state to the undo stack
            self.redo_stack.clear()  # Clear the redo stack

    def rotate_image(self):
        # Rotate the cropped image by 90 degrees
        if self.cropped_image is not None:
            self.cropped_image = cv2.rotate(self.cropped_image, cv2.ROTATE_90_CLOCKWISE)  # Rotate the image
            self.display_image(self.cropped_image, self.cropped_canvas)  # Display the rotated image
            self.undo_stack.append({"original_image": self.image.copy(), "cropped_image": self.cropped_image.copy(), "original_cropped": self.original_cropped.copy()})  # Save the state to the undo stack
            self.redo_stack.clear()  # Clear the redo stack

    def save_image(self):
        # Save the cropped image to a file
        if self.cropped_image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg")])  # Open save file dialog
            if file_path:
                cv2.imwrite(file_path, cv2.cvtColor(self.cropped_image, cv2.COLOR_BGR2RGB))  # Save the image
                messagebox.showinfo("Success", "Image saved successfully.")  # Show success message
        else:
            messagebox.showwarning("Warning", "No image to save.")  # Show warning if no image is available

    def undo(self):
        # Undo the last operation
        if len(self.undo_stack) > 1:
            current_state = self.undo_stack.pop()  # Pop the current state from the undo stack
            self.redo_stack.append(current_state)  # Push the current state to the redo stack
            previous_state = self.undo_stack[-1]  # Get the previous state

            self.image = previous_state["original_image"].copy()  # Restore the original image
            self.display_image(self.image, self.canvas)  # Display the original image

            cropped_image = previous_state.get("cropped_image")  # Get the cropped image from the previous state
            if cropped_image is not None:
                self.cropped_image = cropped_image.copy()  # Restore the cropped image
                self.original_cropped = previous_state.get("original_cropped").copy()  # Restore the original cropped image
                self.display_image(self.cropped_image, self.cropped_canvas)  # Display the cropped image
            else:
                self.cropped_image = None  # Clear the cropped image
                self.original_cropped = None  # Clear the original cropped image
                self.display_image(None, self.cropped_canvas)  # Clear the cropped canvas

        else:
            if self.undo_stack:
                initial_state = self.undo_stack[0]  # Get the initial state
                self.image = initial_state["original_image"].copy()  # Restore the initial image
                self.display_image(self.image, self.canvas)  # Display the initial image
                self.cropped_image = None  # Clear the cropped image
                self.original_cropped = None  # Clear the original cropped image
                self.display_image(None, self.cropped_canvas)  # Clear the cropped canvas
            else:
                messagebox.showinfo("Info", "Nothing to undo.")  # Show info if nothing to undo

    def redo(self):
        # Redo the last undone operation
        if self.redo_stack:
            image_state = self.redo_stack.pop()  # Pop the state from the redo stack
            self.undo_stack.append(image_state)  # Push the state to the undo stack

            self.image = image_state["original_image"].copy()  # Restore the original image
            self.display_image(self.image, self.canvas)  # Display the original image

            cropped_image = image_state.get("cropped_image")  # Get the cropped image from the state
            if cropped_image is not None:
                self.cropped_image = cropped_image.copy()  # Restore the cropped image
                self.original_cropped = image_state.get("original_cropped").copy()  # Restore the original cropped image
                self.display_image(self.cropped_image, self.cropped_canvas)  # Display the cropped image
            else:
                self.cropped_image = None  # Clear the cropped image
                self.original_cropped = None  # Clear the original cropped image
                self.display_image(None, self.cropped_canvas)  # Clear the cropped canvas
        else:
            messagebox.showinfo("Info", "Nothing to redo.")  # Show info if nothing to redo

    def on_window_resize(self, event):
        # Handle window resize event
        if self.image is not None:
            self.display_image(self.image, self.canvas)  # Redisplay the original image
        if self.cropped_image is not None:
            self.display_image(self.cropped_image, self.cropped_canvas)  # Redisplay the cropped image

    def on_closing(self):
        # Handle window closing event
        if messagebox.askokcancel("Quit", "Do you want to quit?"):  # Show confirmation dialog
            self.root.destroy()  # Close the window

# Entry point of the application
if __name__ == "__main__":
    root = tk.Tk()  # Create the main Tkinter window
    app = ImageProcessingApp(root)  # Initialize the application
    root.mainloop()  # Start the Tkinter event loop