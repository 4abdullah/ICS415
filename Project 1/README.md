# **Project 1: Ray Tracing Renderer**

## **Description**
Project 1 is a Python-based ray tracing renderer that simulates the way light interacts with objects to generate realistic 3D images. It employs mathematical models to calculate reflections, lighting, and shading, producing visually accurate renderings. This project is implemented using **NumPy** and **Matplotlib** to handle vector calculations and image rendering efficiently.

---

## **Installation**
Follow the instructions below to set up and install Project 1 on your system.

### **Windows**
1. **Download and Install Python** (if not installed)
   - Visit [Python.org](https://www.python.org/downloads/) and download the latest Python 3 version.
   - Ensure you select the option **"Add Python to PATH"** during installation.

2. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Project1.git
   ```

3. **Navigate to the project directory**
   ```bash
   cd Project1
   ```

4. **Create a virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

5. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

6. **Run the project**
   ```bash
   python project1.py
   ```

### **macOS**
1. **Download and Install Python** (if not installed)
   ```bash
   brew install python
   ```

2. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Project1.git
   ```

3. **Navigate to the project directory**
   ```bash
   cd Project1
   ```

4. **Create a virtual environment (optional but recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

6. **Run the project**
   ```bash
   python project1.py
   ```

### **Linux**
1. **Download and Install Python** (if not installed)
   ```bash
   sudo apt update && sudo apt install python3 python3-venv python3-pip -y
   ```

2. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Project1.git
   ```

3. **Navigate to the project directory**
   ```bash
   cd Project1
   ```

4. **Create a virtual environment (optional but recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

6. **Run the project**
   ```bash
   python project1.py
   ```

---

## **Troubleshooting**
Below are some common issues and their solutions when installing or running Project 1.

### **1. Python Not Recognized**
**Error Message:**
```bash
'python' is not recognized as an internal or external command
```
**Solution:**
- Ensure Python is installed correctly and added to the system PATH.
- Try using `python3` instead of `python`.
- Restart your terminal or command prompt.

### **2. Permission Denied Errors (Linux/macOS)**
**Error Message:**
```bash
Permission denied: ./venv/bin/activate
```
**Solution:**
- Try running the command with `sudo`:
  ```bash
  sudo chmod +x venv/bin/activate
  ```
- If using `pip`, try:
  ```bash
  sudo pip install -r requirements.txt
  ```

### **3. Virtual Environment Not Activating**
**Windows:**
```bash
venv\Scripts\activate : File cannot be loaded because running scripts is disabled on this system.
```
**Solution:**
- Run PowerShell as Administrator and execute:
  ```powershell
  Set-ExecutionPolicy Unrestricted -Scope Process
  ```
- Then activate the environment again:
  ```bash
  venv\Scripts\activate
  ```

### **4. Module Not Found Errors**
**Error Message:**
```bash
ModuleNotFoundError: No module named 'numpy'
```
**Solution:**
- Ensure dependencies are installed correctly:
  ```bash
  pip install -r requirements.txt
  ```
- If the issue persists, reinstall the virtual environment:
  ```bash
  rm -rf venv  # (Linux/macOS)
  rmdir /s /q venv  # (Windows)
  python -m venv venv
  source venv/bin/activate  # (Linux/macOS)
  venv\Scripts\activate  # (Windows)
  pip install -r requirements.txt
  ```
