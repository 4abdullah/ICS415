# Project 2: Shader-Based Ray Tracing Renderer

## Description
Project 2 is an advanced implementation of ray tracing using **GLSL shaders**. Unlike Project 1, which relied on CPU-based computations with NumPy and Matplotlib, this project utilizes **OpenGL shaders (GLSL)** to achieve real-time rendering performance. By leveraging GPU parallelism, this implementation significantly improves rendering speed while maintaining high-quality reflections, lighting, and shading effects.

---

## Installation
Follow the instructions below to set up and install Project 2 on your system.

### **Prerequisites**
Before proceeding, ensure you have the following installed:
- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **pip** (Python package manager)
- **glfw** (for window management)
- **PyOpenGL** (for OpenGL bindings in Python)
- **NumPy** (for numerical operations)

To install the necessary dependencies, run:
```bash
pip install -r requirements.txt
```

### **Windows Installation**
1. **Install Python** (if not installed):
   - Download from [Python.org](https://www.python.org/downloads/)
   - During installation, enable the option **"Add Python to PATH"**

2. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Project2.git
   ```

3. **Navigate to the project directory:**
   ```bash
   cd Project2
   ```

4. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

5. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

6. **Run the project:**
   ```bash
   python main.py
   ```

### **macOS Installation**
1. **Install Python** (if not installed):
   ```bash
   brew install python
   ```

2. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Project2.git
   ```

3. **Navigate to the project directory:**
   ```bash
   cd Project2
   ```

4. **Create a virtual environment (optional but recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

6. **Run the project:**
   ```bash
   python main.py
   ```

### **Linux Installation**
1. **Install Python** (if not installed):
   ```bash
   sudo apt update && sudo apt install python3 python3-venv python3-pip -y
   ```

2. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Project2.git
   ```

3. **Navigate to the project directory:**
   ```bash
   cd Project2
   ```

4. **Create a virtual environment (optional but recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

6. **Run the project:**
   ```bash
   python main.py
   ```

---

## Troubleshooting
Below are common issues and their solutions when installing or running Project 2.

### **1. OpenGL Errors (GLFW not found or not initialized)**
**Error Message:**
```bash
GLFWError: Failed to initialize GLFW
```
**Solution:**
- Ensure you have **GLFW** installed correctly.
- Try reinstalling it manually:
  ```bash
  pip uninstall glfw
  pip install glfw
  ```
- If running on Linux, ensure you have the required OpenGL packages:
  ```bash
  sudo apt install libglfw3 libglfw3-dev
  ```

### **2. Shader Compilation Errors**
**Error Message:**
```bash
RuntimeError: Shader compile error: <specific error details>
```
**Solution:**
- Ensure your **GPU supports OpenGL shaders**.
- Debug the shader code using **glGetShaderInfoLog()**.
- Verify that **vertex_shader.glsl** and **fragment_shader.glsl** files are properly loaded.

### **3. Missing Dependencies**
**Error Message:**
```bash
ModuleNotFoundError: No module named 'OpenGL'
```
**Solution:**
- Ensure dependencies are installed correctly:
  ```bash
  pip install -r requirements.txt
  ```
- If the issue persists, manually install missing modules:
  ```bash
  pip install PyOpenGL glfw numpy
  ```
