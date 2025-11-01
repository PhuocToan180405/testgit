import tkinter as tk
from tkinter import ttk, messagebox
import math
import time

class Node:
    def __init__(self, value=None, node_id=None, is_leaf=True):
        self.value = value
        self.id = node_id
        self.children = []
        self.parent = None
        self.is_leaf = is_leaf
        self.minimax_value = None
        self.alpha = None
        self.beta = None
        self.is_pruned = False
        self.is_best_path = False
        self.visited = False
        self.is_current = False
        
class MinimaxSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Mô Phỏng Thuật Toán Minimax & Alpha-Beta Pruning")
        self.root.geometry("1400x950")
        
        self.tree_root = None
        self.node_counter = 0
        self.selected_node = None
        self.canvas_nodes = {}
        self.algorithm_mode = "minimax"
        self.max_depth = 0
        self.is_root_max = True
        
        self.execution_steps = []
        self.current_step = 0
        self.is_running = False
        self.animation_speed = 500
        
        self.setup_ui()
        self.create_default_tree()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        control_frame = ttk.LabelFrame(main_frame, text="Điều Khiển", padding="5")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=3, pady=3)
        
        # Row 1: Algorithm and Root Layer
        row1_frame = ttk.Frame(control_frame)
        row1_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(row1_frame, text="Thuật toán:", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=3)
        self.algo_var = tk.StringVar(value="minimax")
        ttk.Radiobutton(row1_frame, text="Minimax", variable=self.algo_var, 
                       value="minimax", command=self.on_algorithm_change).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(row1_frame, text="Alpha-Beta", variable=self.algo_var,
                       value="alphabeta", command=self.on_algorithm_change).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(row1_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)
        
        ttk.Label(row1_frame, text="Gốc:", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=3)
        self.root_layer_var = tk.StringVar(value="MAX")
        ttk.Radiobutton(row1_frame, text="MAX", variable=self.root_layer_var, 
                       value="MAX", command=self.on_root_layer_change).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(row1_frame, text="MIN", variable=self.root_layer_var,
                       value="MIN", command=self.on_root_layer_change).pack(side=tk.LEFT, padx=2)
        
        # Row 2: Node operations and Execution controls
        row2_frame = ttk.Frame(control_frame)
        row2_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Button(row2_frame, text="➕ Thêm", width=8,
                  command=self.add_child_node).pack(side=tk.LEFT, padx=2)
        ttk.Button(row2_frame, text="❌ Xóa", width=7,
                  command=self.delete_node).pack(side=tk.LEFT, padx=2)
        ttk.Button(row2_frame, text="✏️ Sửa", width=7,
                  command=self.edit_value).pack(side=tk.LEFT, padx=2)
        ttk.Button(row2_frame, text="🔄 Reset", width=8,
                  command=self.reset_tree).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(row2_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)
        
        self.run_auto_btn = ttk.Button(row2_frame, text="▶️ Tự Động", width=10,
                  command=self.run_algorithm_auto)
        self.run_auto_btn.pack(side=tk.LEFT, padx=2)
        
        self.step_btn = ttk.Button(row2_frame, text="⏭️ Từng Bước", width=10,
                  command=self.run_step)
        self.step_btn.pack(side=tk.LEFT, padx=2)
        
        self.pause_btn = ttk.Button(row2_frame, text="⏸️ Dừng", width=8,
                  command=self.pause_execution, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=2)
        
        self.reset_exec_btn = ttk.Button(row2_frame, text="🔄 Reset TT", width=10,
                  command=self.reset_algorithm)
        self.reset_exec_btn.pack(side=tk.LEFT, padx=2)
        
        # Canvas for tree visualization
        canvas_frame = ttk.LabelFrame(main_frame, text="Sơ Đồ Cây", padding="5")
        canvas_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=3, pady=3)
        
        self.canvas = tk.Canvas(canvas_frame, bg="white", width=1350, height=550)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Sẵn sàng. Chọn node và thao tác hoặc chạy thuật toán!", 
                                     font=("Arial", 9), foreground="blue")
        self.status_label.grid(row=2, column=0, pady=3)
        
        # Status table
        table_frame = ttk.LabelFrame(main_frame, text="Bảng Trạng Thái", padding="5")
        table_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=3, pady=3)
        
        # Create Treeview for status
        columns = ("Node", "Lớp", "Giá Trị Lá", "Minimax", "Alpha", "Beta", "Trạng Thái")
        self.tree_view = ttk.Treeview(table_frame, columns=columns, show="headings", height=6)
        
        for col in columns:
            self.tree_view.heading(col, text=col)
            self.tree_view.column(col, width=110)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree_view.yview)
        self.tree_view.configure(yscroll=scrollbar.set)
        
        self.tree_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Result label
        self.result_label = ttk.Label(main_frame, text="", font=("Arial", 11, "bold"))
        self.result_label.grid(row=4, column=0, pady=5)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=2)
        main_frame.rowconfigure(3, weight=1)
        
    def on_root_layer_change(self):
        self.is_root_max = (self.root_layer_var.get() == "MAX")
        self.reset_algorithm()
        self.draw_tree()
        
    def create_default_tree(self):
        self.tree_root = Node(node_id=self.get_next_id(), is_leaf=False)
        
        for i in range(3):
            child = Node(node_id=self.get_next_id(), is_leaf=False)
            child.parent = self.tree_root
            self.tree_root.children.append(child)
            
            values = [[3, 12, 8], [2, 4, 6], [14, 5, 2]]
            for val in values[i]:
                leaf = Node(value=val, node_id=self.get_next_id(), is_leaf=True)
                leaf.parent = child
                child.children.append(leaf)
        
        self.calculate_depth()
        self.draw_tree()
        
    def get_next_id(self):
        node_id = chr(65 + self.node_counter) if self.node_counter < 26 else f"N{self.node_counter}"
        self.node_counter += 1
        return node_id
        
    def calculate_depth(self):
        def depth(node):
            if not node.children:
                return 0
            return 1 + max(depth(child) for child in node.children)
        self.max_depth = depth(self.tree_root) if self.tree_root else 0
        
    def get_node_layer_type(self, node):
        depth = self.get_node_depth(node)
        if self.is_root_max:
            return "MAX" if depth % 2 == 0 else "MIN"
        else:
            return "MIN" if depth % 2 == 0 else "MAX"
        
    def get_node_depth(self, node):
        depth = 0
        current = node
        while current.parent:
            depth += 1
            current = current.parent
        return depth
        
    def draw_tree(self):
        self.canvas.delete("all")
        self.canvas_nodes.clear()
        
        if not self.tree_root:
            return
            
        self.calculate_depth()
        canvas_width = self.canvas.winfo_width() or 1350
        canvas_height = self.canvas.winfo_height() or 450
        
        def draw_node(node, x, y, width, depth):
            if node.children:
                child_width = width / len(node.children)
                for i, child in enumerate(node.children):
                    child_x = x - width/2 + child_width * i + child_width/2
                    child_y = y + 80
                    
                    line_color = "#2ecc71" if (node.is_best_path and child.is_best_path) else "#bdc3c7"
                    line_width = 3 if (node.is_best_path and child.is_best_path) else 1
                    
                    self.canvas.create_line(x, y+25, child_x, child_y-25, 
                                          fill=line_color, width=line_width)
                    draw_node(child, child_x, child_y, child_width, depth+1)
            
            if node.is_current:
                color = "#9b59b6"
            elif node.is_best_path:
                color = "#2ecc71"
            elif node.is_pruned:
                color = "#e74c3c"
            elif node.visited:
                color = "#f39c12"
            elif node.is_leaf:
                color = "#3498db"
            else:
                color = "#ecf0f1"
            
            radius = 25
            oval = self.canvas.create_oval(x-radius, y-radius, x+radius, y+radius,
                                          fill=color, outline="#34495e", width=2)
            
            label = node.id
            if node.is_leaf and node.value is not None:
                label = f"{node.id}\n{node.value}"
            elif node.minimax_value is not None:
                label = f"{node.id}\n{node.minimax_value}"
            
            text = self.canvas.create_text(x, y, text=label, font=("Arial", 10, "bold"))
            
            layer_type = self.get_node_layer_type(node)
            self.canvas.create_text(x, y-40, text=layer_type, 
                                   font=("Arial", 9, "bold"), fill="#2c3e50")
            
            self.canvas_nodes[oval] = node
            self.canvas_nodes[text] = node
        
        start_x = canvas_width / 2
        start_y = 50
        draw_node(self.tree_root, start_x, start_y, canvas_width - 100, 0)
        
    def on_canvas_click(self, event):
        item = self.canvas.find_closest(event.x, event.y)[0]
        if item in self.canvas_nodes:
            self.selected_node = self.canvas_nodes[item]
            self.highlight_selected()
            self.status_label.config(text=f"Đã chọn node {self.selected_node.id}")
            
    def highlight_selected(self):
        self.draw_tree()
        if self.selected_node:
            for item, node in self.canvas_nodes.items():
                if node == self.selected_node and self.canvas.type(item) == "oval":
                    self.canvas.itemconfig(item, width=4, outline="#e67e22")
                    
    def add_child_node(self):
        if not self.selected_node:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một node trước!")
            return
            
        if self.selected_node.is_leaf:
            self.selected_node.is_leaf = False
            self.selected_node.value = None
            
        new_node = Node(value=0, node_id=self.get_next_id(), is_leaf=True)
        new_node.parent = self.selected_node
        self.selected_node.children.append(new_node)
        
        self.calculate_depth()
        self.draw_tree()
        self.status_label.config(text=f"Đã thêm node con vào {self.selected_node.id}")
        
    def delete_node(self):
        if not self.selected_node:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một node để xóa!")
            return
            
        if self.selected_node == self.tree_root:
            messagebox.showwarning("Cảnh báo", "Không thể xóa node gốc!")
            return
            
        parent = self.selected_node.parent
        parent.children.remove(self.selected_node)
        
        if not parent.children:
            parent.is_leaf = True
            parent.value = 0
            
        self.status_label.config(text=f"Đã xóa node {self.selected_node.id}")
        self.selected_node = None
        self.calculate_depth()
        self.draw_tree()
        
    def edit_value(self):
        if not self.selected_node:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một node!")
            return
            
        if not self.selected_node.is_leaf:
            messagebox.showwarning("Cảnh báo", "Chỉ có thể chỉnh giá trị của node lá!")
            return
            
        dialog = tk.Toplevel(self.root)
        dialog.title("Chỉnh Giá Trị")
        dialog.geometry("300x150")
        
        ttk.Label(dialog, text=f"Nhập giá trị mới cho node {self.selected_node.id}:").pack(pady=10)
        value_entry = ttk.Entry(dialog, font=("Arial", 12))
        value_entry.pack(pady=10)
        value_entry.insert(0, str(self.selected_node.value or 0))
        value_entry.focus()
        
        def save_value():
            try:
                new_value = int(value_entry.get())
                self.selected_node.value = new_value
                self.draw_tree()
                self.status_label.config(text=f"Đã cập nhật giá trị node {self.selected_node.id} = {new_value}")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Lỗi", "Vui lòng nhập số nguyên hợp lệ!")
                
        ttk.Button(dialog, text="💾 Lưu", command=save_value).pack(pady=10)
        value_entry.bind('<Return>', lambda e: save_value())
        
    def reset_tree(self):
        self.node_counter = 0
        self.selected_node = None
        self.create_default_tree()
        self.reset_algorithm()
        self.status_label.config(text="Đã reset cây về trạng thái mặc định!")
        
    def on_algorithm_change(self):
        self.algorithm_mode = self.algo_var.get()
        self.reset_algorithm()
        
    def reset_algorithm(self):
        def reset_node(node):
            node.minimax_value = None
            node.alpha = None
            node.beta = None
            node.is_pruned = False
            node.is_best_path = False
            node.visited = False
            node.is_current = False
            for child in node.children:
                reset_node(child)
                
        if self.tree_root:
            reset_node(self.tree_root)
            
        self.execution_steps = []
        self.current_step = 0
        self.is_running = False
        
        self.run_auto_btn.config(state=tk.NORMAL)
        self.step_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        
        self.draw_tree()
        self.update_status_table()
        self.result_label.config(text="")
        self.status_label.config(text="Đã reset thuật toán. Sẵn sàng chạy lại!")
        
    def prepare_execution(self):
        self.reset_algorithm()
        self.execution_steps = []
        
        if self.algorithm_mode == "minimax":
            self.prepare_minimax_steps(self.tree_root, 0, self.is_root_max)
        else:
            self.prepare_alphabeta_steps(self.tree_root, 0, self.is_root_max, -math.inf, math.inf)
            
        self.execution_steps.append(("mark_path", None, None))
        
    def prepare_minimax_steps(self, node, depth, is_maximizing):
        self.execution_steps.append(("visit", node, is_maximizing))
        
        if node.is_leaf:
            self.execution_steps.append(("leaf", node, node.value))
            return node.value
            
        if is_maximizing:
            max_eval = -math.inf
            for child in node.children:
                eval_score = self.prepare_minimax_steps(child, depth + 1, False)
                max_eval = max(max_eval, eval_score)
            self.execution_steps.append(("internal", node, max_eval))
            return max_eval
        else:
            min_eval = math.inf
            for child in node.children:
                eval_score = self.prepare_minimax_steps(child, depth + 1, True)
                min_eval = min(min_eval, eval_score)
            self.execution_steps.append(("internal", node, min_eval))
            return min_eval
            
    def prepare_alphabeta_steps(self, node, depth, is_maximizing, alpha, beta):
        self.execution_steps.append(("visit_ab", node, (is_maximizing, alpha, beta)))
        
        if node.is_leaf:
            self.execution_steps.append(("leaf", node, node.value))
            return node.value
            
        if is_maximizing:
            max_eval = -math.inf
            for i, child in enumerate(node.children):
                eval_score = self.prepare_alphabeta_steps(child, depth + 1, False, alpha, beta)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    for remaining in node.children[i+1:]:
                        self.execution_steps.append(("prune", remaining, None))
                    break
            self.execution_steps.append(("internal", node, max_eval))
            return max_eval
        else:
            min_eval = math.inf
            for i, child in enumerate(node.children):
                eval_score = self.prepare_alphabeta_steps(child, depth + 1, True, alpha, beta)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    for remaining in node.children[i+1:]:
                        self.execution_steps.append(("prune", remaining, None))
                    break
            self.execution_steps.append(("internal", node, min_eval))
            return min_eval
            
    def run_algorithm_auto(self):
        if not self.tree_root:
            messagebox.showwarning("Cảnh báo", "Không có cây để chạy!")
            return
            
        if not self.execution_steps:
            self.prepare_execution()
            self.current_step = 0
            
        self.is_running = True
        self.run_auto_btn.config(state=tk.DISABLED)
        self.step_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        
        self.execute_next_step_auto()
        
    def execute_next_step_auto(self):
        if not self.is_running or self.current_step >= len(self.execution_steps):
            if self.current_step >= len(self.execution_steps):
                self.finish_execution()
            return
            
        self.execute_step(self.current_step)
        self.current_step += 1
        
        if self.current_step < len(self.execution_steps):
            self.root.after(self.animation_speed, self.execute_next_step_auto)
        else:
            self.finish_execution()
            
    def run_step(self):
        if not self.tree_root:
            messagebox.showwarning("Cảnh báo", "Không có cây để chạy!")
            return
            
        if not self.execution_steps:
            self.prepare_execution()
            self.current_step = 0
            
        if self.current_step < len(self.execution_steps):
            self.execute_step(self.current_step)
            self.current_step += 1
            
            if self.current_step >= len(self.execution_steps):
                self.finish_execution()
        else:
            self.status_label.config(text="Đã hoàn thành tất cả các bước!")
            
    def execute_step(self, step_idx):
        step_type, node, data = self.execution_steps[step_idx]
        
        if step_idx > 0:
            prev_type, prev_node, _ = self.execution_steps[step_idx - 1]
            if prev_node:
                prev_node.is_current = False
        
        if step_type == "visit":
            node.is_current = True
            node.visited = True
            layer = "MAX" if data else "MIN"
            self.status_label.config(text=f"Thăm node {node.id} (lớp {layer})")
            
        elif step_type == "visit_ab":
            node.is_current = True
            node.visited = True
            is_max, alpha, beta = data
            node.alpha = alpha
            node.beta = beta
            layer = "MAX" if is_max else "MIN"
            self.status_label.config(text=f"Thăm node {node.id} (lớp {layer})")
            
        elif step_type == "leaf":
            node.minimax_value = data
            node.is_current = True
            self.status_label.config(text=f"Node lá {node.id} có giá trị {data}")
            
        elif step_type == "internal":
            node.minimax_value = data
            node.is_current = True
            self.status_label.config(text=f"Node {node.id} tính được giá trị {data}")
            
        elif step_type == "prune":
            self.mark_pruned(node)
            self.status_label.config(text=f"Cắt nhánh từ node {node.id}")
            
        elif step_type == "mark_path":
            self.mark_best_path()
            algo_name = "Minimax" if self.algorithm_mode == "minimax" else "Alpha-Beta Pruning"
            result = self.tree_root.minimax_value
            self.result_label.config(
                text=f"✓ Hoàn thành! Thuật toán {algo_name}\n" +
                     f"Kết quả: {result} | Đường đi tối ưu: màu xanh lá",
                foreground="green"
            )
            self.status_label.config(text=f"Đánh dấu đường đi tối ưu")
            
        self.draw_tree()
        self.update_status_table()
        
    def mark_pruned(self, node):
        node.is_pruned = True
        for child in node.children:
            self.mark_pruned(child)
            
    def mark_best_path(self):
        if not self.tree_root:
            return
            
        def mark_path(node):
            node.is_best_path = True
            if node.is_leaf:
                return
                
            is_max = self.get_node_layer_type(node) == "MAX"
            
            best_child = None
            if is_max:
                best_value = -math.inf
                for child in node.children:
                    if child.minimax_value is not None and child.minimax_value > best_value:
                        best_value = child.minimax_value
                        best_child = child
            else:
                best_value = math.inf
                for child in node.children:
                    if child.minimax_value is not None and child.minimax_value < best_value:
                        best_value = child.minimax_value
                        best_child = child
                        
            if best_child:
                mark_path(best_child)
                
        mark_path(self.tree_root)
        
    def pause_execution(self):
        self.is_running = False
        self.run_auto_btn.config(state=tk.NORMAL)
        self.step_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Đã tạm dừng. Có thể tiếp tục chạy từng bước hoặc tự động.")
        
    def finish_execution(self):
        self.is_running = False
        self.run_auto_btn.config(state=tk.DISABLED)
        self.step_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.DISABLED)
        
    def update_status_table(self):
        for item in self.tree_view.get_children():
            self.tree_view.delete(item)
            
        if not self.tree_root:
            return
            
        def add_to_table(node):
            layer = self.get_node_layer_type(node)
            leaf_val = str(node.value) if node.is_leaf and node.value is not None else "-"
            minimax_val = str(node.minimax_value) if node.minimax_value is not None else "-"
            
            alpha_str = "-"
            beta_str = "-"
            if self.algorithm_mode == "alphabeta":
                if node.alpha is not None:
                    alpha_str = str(node.alpha) if node.alpha != -math.inf else "-∞"
                if node.beta is not None:
                    beta_str = str(node.beta) if node.beta != math.inf else "+∞"
            
            status = []
            if node.is_current:
                status.append("Đang xét")
            elif node.is_best_path:
                status.append("Đường tối ưu")
            elif node.is_pruned:
                status.append("Đã cắt")
            elif node.visited:
                status.append("Đã thăm")
            else:
                status.append("Chưa thăm")
                
            status_str = ", ".join(status)
            
            values = (node.id, layer, leaf_val, minimax_val, alpha_str, beta_str, status_str)
            item = self.tree_view.insert("", tk.END, values=values)
            
            if node.is_current:
                self.tree_view.item(item, tags=('current',))
            elif node.is_best_path:
                self.tree_view.item(item, tags=('best',))
            elif node.is_pruned:
                self.tree_view.item(item, tags=('pruned',))
            elif node.visited:
                self.tree_view.item(item, tags=('visited',))
                
            for child in node.children:
                add_to_table(child)
                
        add_to_table(self.tree_root)
        
        self.tree_view.tag_configure('current', background='#d8b5e8')
        self.tree_view.tag_configure('best', background='#a9dfbf')
        self.tree_view.tag_configure('pruned', background='#f5b7b1')
        self.tree_view.tag_configure('visited', background='#fad7a0')

def main():
    root = tk.Tk()
    app = MinimaxSimulator(root)
    root.mainloop()

if __name__ == "__main__":
    main()