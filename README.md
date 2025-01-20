# ICS415
# README: How to Run Python Code in Visual Studio Code

This guide provides clear instructions on how to set up and run Python code in Visual Studio Code (VS Code).

---

## Prerequisites

1. **Install Python**:
   - Download and install Python from the official website: [https://www.python.org/downloads/](https://www.python.org/downloads/).
   - During installation, ensure you check the option to add Python to your PATH.

2. **Install Visual Studio Code**:
   - Download and install VS Code from: [https://code.visualstudio.com/](https://code.visualstudio.com/).

3. **Install the Python Extension for VS Code**:
   - Open VS Code.
   - Access the Extensions view by clicking the Extensions icon in the sidebar or pressing `Ctrl+Shift+X`.
   - Search for "Python" and install the official extension by Microsoft.

---

## Steps to Run Python Code

1. **Open Your Python File**:
   - Launch VS Code.
   - Open the folder containing your Python files or directly open the `.py` file you want to execute.

2. **Select the Python Interpreter**:
   - Press `Ctrl+Shift+P` to open the Command Palette.
   - Type `Python: Select Interpreter` and select the option.
   - Choose the Python version you installed (e.g., Python 3.x).

3. **Run the Python Code**:
   - Open your `.py` file in the editor.
   - Click the "Run" button (a triangle ▶ icon) in the top-right corner of the editor, or:
     - Right-click in the editor and choose "Run Python File in Terminal."
     - Press `Ctrl+F5` to run without debugging or `F5` to run with debugging.

4. **View Output**:
   - Check the terminal at the bottom of the VS Code window to see the output of your code.

---

## Optional: Virtual Environment Setup

To manage project-specific dependencies, set up a virtual environment:

1. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   ```

2. **Activate the Virtual Environment**:
   - **Windows**: `venv\Scripts\activate`
   - **macOS/Linux**: `source venv/bin/activate`

3. **Install Dependencies**:
   ```bash
   pip install <package-name>
   ```

4. **Use the Virtual Environment in VS Code**:
   - Follow Step 2 from "Steps to Run Python Code" to select the interpreter located in the `venv` directory.

---

## Troubleshooting

- **Python Interpreter Not Found**: Ensure Python is correctly installed and added to your PATH.
- **Python Extension Issues**: Make sure the Python extension is installed and enabled in VS Code.
- **Changes Not Reflected**: Restart VS Code to apply new configurations.

---

