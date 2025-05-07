import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re
import os
import io
from PIL import Image

class MarkdownTableVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Markdown Table Visualizer")
        self.root.geometry("1200x700")
        self.root.minsize(800, 600)
        
        # Set up the main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create split panes
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Markdown input
        self.left_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.left_frame, weight=1)
        
        # Right side - Table visualization
        self.right_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.right_frame, weight=1)
        
        self.setup_left_frame()
        self.setup_right_frame()
        self.setup_bottom_frame()
        
        # Add sample table for demonstration
        self.markdown_input.insert(tk.END, """| Name | Age | City |
|------|-----|------|
| John | 30  | New York |
| Alice | 25 | London |
| Bob | 35 | Paris |
| Eve | 28 | Tokyo |""")
        
        # Initial render
        self.render_table()
        
    def setup_left_frame(self):
        # Title
        self.left_title = ttk.Label(self.left_frame, text="Markdown Table Input", font=("Arial", 12, "bold"))
        self.left_title.pack(pady=(0, 5), fill=tk.X)
        
        # Markdown input
        self.input_frame = ttk.Frame(self.left_frame)
        self.input_frame.pack(fill=tk.BOTH, expand=True)
        
        self.markdown_input = tk.Text(self.input_frame, wrap=tk.WORD, font=("Courier", 12))
        self.markdown_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar for text input
        self.input_scrollbar = ttk.Scrollbar(self.input_frame, command=self.markdown_input.yview)
        self.input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.markdown_input.config(yscrollcommand=self.input_scrollbar.set)
        
        # Button to render table
        self.render_button = ttk.Button(self.left_frame, text="Render Table", command=self.render_table)
        self.render_button.pack(pady=10, fill=tk.X)
        
    def setup_right_frame(self):
        # Title
        self.right_title = ttk.Label(self.right_frame, text="Table Visualization", font=("Arial", 12, "bold"))
        self.right_title.pack(pady=(0, 5), fill=tk.X)
        
        # Frame for visualization
        self.viz_frame = ttk.Frame(self.right_frame)
        self.viz_frame.pack(fill=tk.BOTH, expand=True)
        
        # Initially empty - will be filled by render_table()
        self.fig = plt.Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, self.viz_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        
    def setup_bottom_frame(self):
        # Bottom frame for download and other options
        self.bottom_frame = ttk.Frame(self.main_frame)
        self.bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Styling options frame
        self.style_frame = ttk.LabelFrame(self.bottom_frame, text="Styling Options")
        self.style_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Colors
        self.color_frame = ttk.Frame(self.style_frame)
        self.color_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.color_frame, text="Header Color:").pack(side=tk.LEFT, padx=5)
        self.header_color = ttk.Combobox(self.color_frame, values=["lightblue", "lightgreen", "lightgray", "lightcoral", "lightyellow"])
        self.header_color.set("lightblue")
        self.header_color.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.color_frame, text="Row Colors:").pack(side=tk.LEFT, padx=5)
        self.row_colors = ttk.Combobox(self.color_frame, values=["white,lightgray", "white,lightyellow", "white,lightcyan", "white,white"])
        self.row_colors.set("white,lightgray")
        self.row_colors.pack(side=tk.LEFT, padx=5)
        
        # Text styling
        self.text_frame = ttk.Frame(self.style_frame)
        self.text_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.text_frame, text="Font Size:").pack(side=tk.LEFT, padx=5)
        self.font_size = ttk.Spinbox(self.text_frame, from_=8, to=16, width=3)
        self.font_size.set(10)
        self.font_size.pack(side=tk.LEFT, padx=5)
        
        # Bold headers checkbox
        self.bold_headers_var = tk.BooleanVar(value=True)
        self.bold_headers = ttk.Checkbutton(self.text_frame, text="Bold Headers", variable=self.bold_headers_var)
        self.bold_headers.pack(side=tk.LEFT, padx=5)
        
        # File options frame
        self.file_frame = ttk.Frame(self.bottom_frame)
        self.file_frame.pack(side=tk.RIGHT, fill=tk.X, padx=(5, 0))
        
        # Image format selection
        ttk.Label(self.file_frame, text="Image Format:").pack(side=tk.LEFT, padx=5)
        self.image_format = ttk.Combobox(self.file_frame, values=["PNG", "JPG", "PDF", "SVG"])
        self.image_format.set("PNG")
        self.image_format.pack(side=tk.LEFT, padx=5)
        
        # DPI setting
        ttk.Label(self.file_frame, text="DPI:").pack(side=tk.LEFT, padx=5)
        self.dpi_setting = ttk.Spinbox(self.file_frame, from_=72, to=300, width=4)
        self.dpi_setting.set(150)
        self.dpi_setting.pack(side=tk.LEFT, padx=5)
        
        # Download button
        self.download_button = ttk.Button(self.file_frame, text="Download Image", command=self.download_image)
        self.download_button.pack(side=tk.RIGHT, padx=5)
    
    def parse_markdown_table(self, markdown_text):
        """Parse markdown table into list of lists"""
        lines = markdown_text.strip().split('\n')
        if len(lines) < 3:  # Need at least header, separator, and one data row
            return None, None
        
        # Extract headers
        header_match = re.findall(r'\|(.*?)\|', lines[0])
        if not header_match:
            return None, None
        
        headers = [h.strip() for h in header_match]
        
        # Validate separator line (second line)
        sep_line = lines[1]
        if not all(c in '|-:' for c in sep_line.strip()):
            return None, None
        
        # Extract data rows
        data = []
        for i in range(2, len(lines)):
            row_match = re.findall(r'\|(.*?)\|', lines[i])
            if row_match:
                row_data = [cell.strip() for cell in row_match]
                data.append(row_data)
        
        return headers, data
    
    def render_table(self):
        """Render the markdown table as an image"""
        markdown_text = self.markdown_input.get("1.0", tk.END)
        headers, data = self.parse_markdown_table(markdown_text)
        
        if not headers or not data:
            messagebox.showerror("Error", "Invalid markdown table format")
            return
        
        # Create new figure
        self.fig.clear()
        
        # Get styling options
        header_bg = self.header_color.get()
        row_bg = self.row_colors.get().split(',')
        font_size = int(self.font_size.get())
        bold_headers = self.bold_headers_var.get()
        
        # Create the table
        ax = self.fig.add_subplot(111)
        ax.axis('off')
        
        # Calculate cell text and colors
        cell_text = data
        
        # Create color arrays with proper dimensions
        # Each row in cellColours needs to be a list of colors for each cell in that row
        cell_colors = []
        for i in range(len(data)):
            row_color = row_bg[i % len(row_bg)]
            cell_colors.append([row_color] * len(headers))
        
        # Create the table
        header_props = {
            'fontsize': font_size,
            'fontweight': 'bold' if bold_headers else 'normal'
        }
        
        cell_props = {
            'fontsize': font_size
        }
        
        table = ax.table(
            cellText=cell_text,
            colLabels=headers,
            loc='center',
            cellLoc='center',
            colColours=[header_bg] * len(headers),
            cellColours=cell_colors
        )
        
        # Style the table
        table.auto_set_font_size(False)
        table.scale(1.2, 1.5)  # Adjust table size
        
        # Apply styling to headers
        for i in range(len(headers)):
            cell = table.get_celld()[(0, i)]
            cell.set_text_props(**header_props)
            
        # Apply styling to cells
        for i in range(len(data)):
            for j in range(len(headers)):
                cell = table.get_celld()[(i+1, j)]
                cell.set_text_props(**cell_props)
        
        # Adjust layout
        self.fig.tight_layout()
        
        # Display the table
        self.canvas.draw()
        
    def download_image(self):
        """Save the table as an image file"""
        try:
            # Get image format
            img_format = self.image_format.get().lower()
            dpi = int(self.dpi_setting.get())
            
            # Default file extensions
            extensions = {
                "png": ".png",
                "jpg": ".jpg",
                "pdf": ".pdf",
                "svg": ".svg"
            }
            
            # Get file path from user
            file_path = filedialog.asksaveasfilename(
                defaultextension=extensions[img_format],
                filetypes=[(f"{img_format.upper()} files", f"*{extensions[img_format]}")]
            )
            
            if file_path:
                self.fig.savefig(file_path, format=img_format, dpi=dpi, bbox_inches='tight')
                messagebox.showinfo("Success", f"Image saved successfully to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving image: {str(e)}")
            
    def copy_to_clipboard(self):
        """Copy the table image to clipboard"""
        try:
            # Save figure to buffer
            buf = io.BytesIO()
            self.fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            
            # Convert to PIL Image
            image = Image.open(buf)
            
            # Copy to clipboard (platform-specific)
            if os.name == 'nt':  # Windows
                import win32clipboard
                from io import BytesIO
                
                output = BytesIO()
                image.convert('RGB').save(output, 'BMP')
                data = output.getvalue()[14:]
                output.close()
                
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                win32clipboard.CloseClipboard()
                
                messagebox.showinfo("Success", "Image copied to clipboard")
            else:
                messagebox.showinfo("Not Supported", "Clipboard copy is only supported on Windows")
        except Exception as e:
            messagebox.showerror("Error", f"Error copying to clipboard: {str(e)}")

def main():
    root = tk.Tk()
    app = MarkdownTableVisualizer(root)
    root.mainloop()

if __name__ == "__main__":
    main()