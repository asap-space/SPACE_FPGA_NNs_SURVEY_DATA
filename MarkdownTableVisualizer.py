import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re

class MarkdownTableVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Markdown Table Visualizer")
        self.root.geometry("1200x700")
        self.root.minsize(800, 600)

        self.current_headers = []
        self.markdown_text = ""
        self.zoom_factor = 1.0
        
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.setup_top_frame()
        self.setup_viz_frame()
        self.setup_bottom_frame()
        
    def setup_top_frame(self):
        self.top_controls = ttk.Frame(self.main_frame)
        self.top_controls.pack(fill=tk.X, pady=(0, 6))

        self.file_button = ttk.Button(self.top_controls, text="Load Markdown File", command=self.load_markdown_file)
        self.file_button.pack(fill=tk.X)
        
    def setup_viz_frame(self):
        self.right_title = ttk.Label(self.main_frame, text="Table Visualization", font=("Arial", 12, "bold"))
        self.right_title.pack(pady=(0, 5), fill=tk.X)
        
        self.viz_frame = ttk.Frame(self.main_frame)
        self.viz_frame.pack(fill=tk.BOTH, expand=True)

        self.viz_canvas = tk.Canvas(self.viz_frame, highlightthickness=0)
        self.viz_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.viz_scrollbar_y = ttk.Scrollbar(self.viz_frame, orient=tk.VERTICAL, command=self.viz_canvas.yview)
        self.viz_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.bottom_scroll_frame = ttk.Frame(self.main_frame)
        self.bottom_scroll_frame.pack(fill=tk.X)
        self.viz_scrollbar_x = ttk.Scrollbar(self.bottom_scroll_frame, orient=tk.HORIZONTAL, command=self.viz_canvas.xview)
        self.viz_scrollbar_x.pack(fill=tk.X)

        self.viz_canvas.configure(yscrollcommand=self.viz_scrollbar_y.set, xscrollcommand=self.viz_scrollbar_x.set)

        self.fig = plt.Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, self.viz_canvas)
        self.canvas_widget = self.canvas.get_tk_widget()
        
        self.canvas_window = self.viz_canvas.create_window((0, 0), window=self.canvas_widget, anchor="nw")

        self.viz_canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas_widget.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas_widget.bind("<Shift-MouseWheel>", self.on_shift_mousewheel)
        
        # Windows / Mac zoom events
        self.canvas_widget.bind("<Control-MouseWheel>", self.on_zoom)
        self.canvas_widget.bind("<Command-MouseWheel>", self.on_zoom)

        # For panning support (drag)
        self.canvas_widget.bind("<ButtonPress-1>", self.start_pan)
        self.canvas_widget.bind("<B1-Motion>", self.pan)
        
    def setup_bottom_frame(self):
        # Bottom frame for download and other options
        self.bottom_frame = ttk.Frame(self.main_frame)
        self.bottom_frame.pack(fill=tk.X, pady=(10, 0))

        self.left_bottom = ttk.Frame(self.bottom_frame)
        self.left_bottom.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Styling options frame
        self.style_frame = ttk.LabelFrame(self.left_bottom, text="Styling Options")
        self.style_frame.pack(fill=tk.X, expand=True)
        
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

        # Column filter frame
        self.column_frame = ttk.LabelFrame(self.left_bottom, text="Column Filter (Hide)")
        self.column_frame.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

        self.column_list_frame = ttk.Frame(self.column_frame)
        self.column_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.column_listbox = tk.Listbox(self.column_list_frame, selectmode=tk.MULTIPLE, height=6)
        self.column_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.column_scrollbar = ttk.Scrollbar(self.column_list_frame, command=self.column_listbox.yview)
        self.column_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.column_listbox.config(yscrollcommand=self.column_scrollbar.set)

        self.column_button_frame = ttk.Frame(self.column_frame)
        self.column_button_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        self.show_all_button = ttk.Button(self.column_button_frame, text="Show All Columns", command=self.show_all_columns)
        self.show_all_button.pack(side=tk.LEFT, padx=(0, 6))

        self.column_listbox.bind("<<ListboxSelect>>", lambda event: self.render_table())
        
        # File options frame
        self.file_frame = ttk.Frame(self.bottom_frame)
        self.file_frame.pack(side=tk.RIGHT, fill=tk.X, padx=(5, 0), pady=(4, 0))
        
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

        header_line = self.normalize_pipe_line(lines[0])
        headers = [h.strip() for h in header_line.split('|')[1:-1]]
        if not headers:
            return None, None
        
        # Validate separator line (second line)
        sep_line = self.normalize_pipe_line(lines[1])
        separators = sep_line.split('|')[1:-1]
        if not all(all(c in '|-:' for c in sep.strip()) for sep in separators):
            return None, None
        
        # Extract data rows
        data = []
        for i in range(2, len(lines)):
            row_line = lines[i].strip()
            if row_line:
                row_line = self.normalize_pipe_line(row_line)
                row_data = [cell.strip() for cell in row_line.split('|')[1:-1]]
                data.append(row_data)
        
        return headers, data

    def normalize_pipe_line(self, line):
        stripped = line.strip()
        if not stripped.startswith('|'):
            stripped = '|' + stripped
        if not stripped.endswith('|'):
            stripped = stripped + '|'
        return stripped
    
    def parse_markdown_formatting(self, text):
        """Parse markdown formatting in text and return formatting info"""
        original_text = text
        processed_text = text
        
        # Formatting settings
        is_bold = False
        is_italic = False
        
        # Check for bold (either **text** or __text__)
        bold_pattern = r'(\*\*|__)(.*?)(\1)'
        bold_match = re.search(bold_pattern, processed_text)
        if bold_match:
            is_bold = True
            # Replace the bold text, preserving the content
            processed_text = re.sub(bold_pattern, lambda m: m.group(2), processed_text)
        
        # Check for italic (either *text* or _text_)
        # But make sure it's not part of a bold marker we already processed
        italic_pattern = r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)|(?<!_)_(?!_)(.+?)(?<!_)_(?!_)'
        italic_match = re.search(italic_pattern, processed_text)
        if italic_match:
            is_italic = True
            # Get the content from whichever group matched
            italic_content = italic_match.group(1) if italic_match.group(1) is not None else italic_match.group(2)
            # Replace the italic text
            processed_text = re.sub(italic_pattern, lambda m: italic_content, processed_text, 1)
        
        return {
            'original': original_text,
            'text': processed_text,
            'weight': 'bold' if is_bold else 'normal',
            'style': 'italic' if is_italic else 'normal'
        }
    
    def render_table(self):
        """Render the markdown table as an image"""
        try:
            markdown_text = self.markdown_text
            if not markdown_text.strip():
                messagebox.showerror("Error", "Load a markdown table file first")
                return
            headers, data = self.parse_markdown_table(markdown_text)
            
            if not headers or not data:
                messagebox.showerror("Error", "Invalid markdown table format")
                return

            self.update_column_filter(headers)
            visible_headers, visible_data = self.apply_column_filter(headers, data)
            if not visible_headers:
                messagebox.showerror("Error", "All columns are hidden. Show at least one column.")
                return
            
            # Create new figure
            self.fig.clear()
            
            # Get styling options
            header_bg = self.header_color.get()
            row_bg = self.row_colors.get().split(',')
            font_size = int(self.font_size.get())
            
            # Create the table
            ax = self.fig.add_subplot(111)
            ax.axis('off')
            
            # Process cell text and formatting
            cell_text = []
            cell_formatting = []
            
            for row in visible_data:
                # Pad row if needed
                while len(row) < len(visible_headers):
                    row.append('')
                
                # Keep only columns that match headers
                row = row[:len(visible_headers)]
                
                # Process text and store formatting
                row_text = []
                row_format = []
                
                for cell in row:
                    formatting = self.parse_markdown_formatting(cell)
                    row_text.append(self.sanitize_cell_text(formatting['text']))
                    row_format.append(formatting)
                
                cell_text.append(row_text)
                cell_formatting.append(row_format)
            
            # Create color arrays with proper dimensions
            cell_colors = []
            for i in range(len(cell_text)):
                row_color = row_bg[i % len(row_bg)]
                cell_colors.append([row_color] * len(visible_headers))
            
            # Calculate column widths and row heights heuristically
            max_col_widths = [max(10, len(h)) for h in visible_headers]
            total_lines = 2 # Header spacing margin
            
            for row in cell_text:
                row_lines = 1
                for i, cell in enumerate(row):
                    lines = cell.split('\n')
                    max_line_len = max([len(line) for line in lines] + [0])
                    if max_line_len > max_col_widths[i]:
                        max_col_widths[i] = max_line_len
                    row_lines = max(row_lines, len(lines))
                total_lines += row_lines
                
            total_chars_width = sum(max_col_widths)
            col_widths = [w / total_chars_width for w in max_col_widths] if total_chars_width > 0 else None
            
            # Size the figure based on text content and zoom factor
            fig_width = max(10.0, total_chars_width * 0.12 * self.zoom_factor)
            fig_height = max(5.0, total_lines * 0.3 * self.zoom_factor)
            self.fig.set_size_inches(fig_width, fig_height)

            # Create the table
            table = ax.table(
                cellText=cell_text,
                colLabels=visible_headers,
                loc='center',
                cellLoc='center',
                colColours=[header_bg] * len(visible_headers),
                cellColours=cell_colors,
                colWidths=col_widths,
                bbox=[0, 0, 1, 1]
            )
            
            # Style the table
            table.auto_set_font_size(False)
            
            # Apply styling to headers (always bold)
            for i in range(len(visible_headers)):
                cell = table.get_celld()[(0, i)]
                cell.set_text_props(fontsize=font_size, fontweight='bold')
                
            # Apply styling to data cells based on markdown formatting
            for i in range(len(cell_text)):
                for j in range(len(visible_headers)):
                    cell = table.get_celld()[(i+1, j)]
                    format_info = cell_formatting[i][j]
                    
                    # Set text properties based on markdown formatting
                    cell.set_text_props(
                        fontsize=font_size,
                        fontweight=format_info['weight'],
                        fontstyle=format_info['style']
                    )
            
            # Adjust layout without tight_layout warnings
            self.fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
            
            # Display the table
            self.canvas.draw()
            self.root.after(0, self.refresh_canvas_view)
        except Exception as e:
            messagebox.showerror("Error", f"Error rendering table: {str(e)}")

    def on_canvas_configure(self, event):
        self.center_canvas_window()

    def update_scroll_region(self):
        self.viz_canvas.configure(scrollregion=self.viz_canvas.bbox("all"))
        self.center_canvas_window()

    def sync_canvas_window_size(self):
        self.canvas_widget.update_idletasks()
        width = int(self.fig.get_figwidth() * self.fig.dpi)
        height = int(self.fig.get_figheight() * self.fig.dpi)
        self.viz_canvas.itemconfigure(self.canvas_window, width=width, height=height)

    def refresh_canvas_view(self):
        self.sync_canvas_window_size()
        self.update_scroll_region()

    def center_canvas_window(self):
        # Prevent layout stalls while panning by relying on winfo_width directly
        canvas_width = self.viz_canvas.winfo_width()
        canvas_height = self.viz_canvas.winfo_height()
        
        bbox = self.viz_canvas.bbox("all")
        if not bbox:
            return
            
        content_width = bbox[2] - bbox[0]
        content_height = bbox[3] - bbox[1]

        x_offset = max(0, int((canvas_width - content_width) / 2))
        y_offset = max(0, int((canvas_height - content_height) / 2))
        
        self.viz_canvas.coords(self.canvas_window, x_offset, y_offset)

    def on_mousewheel(self, event):
        if event.delta:
            self.viz_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_shift_mousewheel(self, event):
        if event.delta:
            self.viz_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_zoom(self, event):
        if event.delta > 0:
            self.zoom_factor *= 1.1
        else:
            self.zoom_factor /= 1.1
            
        # Prevent zooming out too much
        self.zoom_factor = max(0.2, self.zoom_factor)
        self.render_table()

    def start_pan(self, event):
        self.viz_canvas.scan_mark(event.x, event.y)

    def pan(self, event):
        self.viz_canvas.scan_dragto(event.x, event.y, gain=1)

    def sanitize_cell_text(self, text):
        cleaned = text.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
        return cleaned.replace("$", r"\$")

    def update_column_filter(self, headers):
        if headers == self.current_headers:
            return

        self.current_headers = headers
        self.column_listbox.delete(0, tk.END)
        for header in headers:
            self.column_listbox.insert(tk.END, header)

    def apply_column_filter(self, headers, data):
        hidden = {self.column_listbox.get(index) for index in self.column_listbox.curselection()}

        visible_indices = [i for i, header in enumerate(headers) if header not in hidden]
        visible_headers = [headers[i] for i in visible_indices]
        visible_data = []
        for row in data:
            visible_data.append([row[i] if i < len(row) else '' for i in visible_indices])

        return visible_headers, visible_data

    def show_all_columns(self):
        self.column_listbox.selection_clear(0, tk.END)
        self.render_table()
    
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

    def load_markdown_file(self):
        """Load markdown text from a file"""
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*")]
            )
            if not file_path:
                return

            with open(file_path, "r", encoding="utf-8") as handle:
                content = handle.read()

            self.markdown_text = content
            self.render_table()
        except Exception as e:
            messagebox.showerror("Error", f"Error loading file: {str(e)}")

def main():
    root = tk.Tk()
    app = MarkdownTableVisualizer(root)
    root.mainloop()

if __name__ == "__main__":
    main()