
# FiberLab Developer Guide

## 1. Project Overview

FiberLab is an interactive Optical Fiber Communication Simulator built using Python and Streamlit.

It helps users explore optical fiber fundamentals, attenuation, and basic signal propagation through interactive simulations.

## 2. Technology Stack

- Python — Core programming language
- Streamlit — Web application framework
- NumPy and SciPy — Numerical computing
- Plotly — Interactive visualizations
- Matplotlib — Scientific plotting
- Pytest — Automated testing
- Ruff — Code quality and linting
- Git and GitHub — Version control and collaboration

## 3. Project Architecture

FiberLab follows a modular architecture that separates application logic, physics calculations, visualization, and reusable UI components.


## 4. Project Folder Structure

```text
FiberLab/
├── app.py
├── components/
├── pages/
├── physics/
├── visualization/
├── tests/
├── docs/
│   └── integration/
├── .github/
│   └── workflows/
├── requirements.txt
├── README.md
└── .gitignore
```

### 4.1 Folder Responsibilities

- `app.py`: Application entry point and navigation.
- `components/`: Reusable Streamlit UI components.
- `pages/`: Individual simulator pages.
- `physics/`: Scientific calculations and mathematical models.
- `visualization/`: Interactive graphs and visual simulations.
- `tests/`: Automated tests.
- `docs/`: Technical and developer documentation.
- `.github/workflows/`: GitHub Actions and CI configuration.


## 5. Development Environment Setup

### Prerequisites

- Python 3.12 or compatible version.
- Git.
- Visual Studio Code (recommended).

### Clone the Repository

```bash
git clone https://github.com/CodingBunny06/FiberLab.git
cd FiberLab
```

### Create a Virtual Environment

```bash
python3 -m venv .venv
```

### Activate the Environment

macOS/Linux:

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```


## 6. Running FiberLab

Start the application using:

```bash
streamlit run app.py
```

Streamlit will provide a local URL to access the application in your browser.

To stop the application, press `Ctrl + C` in the terminal.


## 7. Development Workflow

All development work should follow the project's Git collaboration process.

### 7.1 Branching Strategy

- `main`: Stable integration branch.
- `feature/`: New features and development work.
- `fix/`: Bug fixes.
- `docs/`: Documentation changes.

Create a feature branch before starting new work:

```bash
git switch main
git pull origin main
git switch -c feature/your-feature-name
```

### 7.2 Development Process

1. Understand the assigned task.
2. Implement the changes.
3. Run code quality checks.
4. Run automated tests.
5. Commit the changes.
6. Push the branch.
7. Open a pull request for review.


## 8. Testing and Code Quality

Before submitting changes, run the following checks.

### Run Ruff

```bash
ruff check .
```

### Run Pytest

```bash
python -m pytest -v
```

All checks must pass before submitting a pull request.

New functionality should include appropriate automated tests.


## 9. Coding Conventions

- Follow consistent Python naming conventions.
- Use meaningful variable and function names.
- Include type hints wherever practical.
- Write docstrings for functions and classes.
- Keep functions focused on a single responsibility.
- Avoid duplicating existing functionality.
- Keep physics calculations independent of Streamlit.
- Keep visualization logic separate from scientific calculations.
- Document units for physical quantities.

## 10. Module Integration Guidelines

FiberLab uses separate modules for scientific calculations and visualizations.

### Physics Module

- Responsible for optical fiber calculations.
- Uses documented physical units.
- Must not depend on Streamlit.
- Must include independent unit tests.

### Visualization Module

- Responsible for graphical representations.
- Uses Plotly for interactive figures.
- Receives calculated data from the physics module.
- Must not duplicate scientific calculations.

### Application Layer

- Collects and validates user inputs.
- Calls physics functions.
- Passes results to visualization functions.
- Displays results through Streamlit.

Refer to `docs/integration/MODULE_CONTRACTS.md`
for detailed function specifications and integration agreements.