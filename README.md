# ImageUI

## Setup

1. **Clone the repository:**
   ```bash { name=git-clone }
   git clone https://github.com/your-username/ImageUI.git
   cd ImageUI
   ```

2. **Create a virtual environment:**
   ```bash { name=create-venv }
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the dependencies:**
   ```bash { name=pip-install }
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash { name=run-app }
   python main.py
   ```

## Run with Runme

All setup and execution commands are available as Runme tasks. You can run them directly from the README.md file using the Runme extension for VS Code or by running `runme run <task-name>` in your terminal.

For example, to run the application:
```bash
runme run run-app
```

## Build for macOS

To create a standalone `.app` file that can be run on other Mac computers:

1. **Build the application:**
   After following the setup steps above, run the following command:
   ```bash { name=build-app }
   python setup.py py2app
   ```
   This will create a `dist` folder containing `ImageUI.app`.

2. **Prepare for Distribution:**
   To share the application, it's best to create a zip archive of the `.app` file.
   ```bash { name=zip-app }
   cd dist
   zip -r ImageResizer.zip ImageResizer.app
   ```
   You can then send the `ImageResizer.app.zip` file to other macOS users. They can unzip it and run `ImageResizer.app` without needing to install Python or any dependencies.
