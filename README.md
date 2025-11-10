## Setup and Installation

### Prerequisites

- A modern web browser with support for the Web Speech API (e.g., Google Chrome).
- Python 3.x installed on your system.
- `pip` for installing Python packages.
- Node.js 14.x or higher (for CNCjs).
- A collection of G-code files (`.nc`), where each file represents a single character.

### 1. Backend Setup (G-code Conversion)

1. **Clone the repository or download the files.**

2. **Install Python dependencies:**
    Open your terminal or command prompt and run the following command to install Flask and Flask-CORS.

    ```bash
    pip install Flask Flask-Cors
    ```

3. **Configure Character Directory:**
    The Python script needs to know where your character G-code (`.nc`) files are located. Open `app.py` and update the following line with the absolute path to your character directory:

    ```python
    # Inside the convert_text_to_gcode() function
    letters = readLetters("C:\\path\\to\\your\\character\\files")
    ```

4. **Run the Flask Server:**
    Execute the following command in your terminal from the project's root directory.

    ```bash
    python app.py
    ```

    The server will start, typically on `http://127.0.0.1:5000`. This server **must** be running for the "Convert text to g-code" button to work.

### 2. CNCjs Setup (G-code Sending)

The "Click to go to G-code sender" button is configured to open a CNCjs instance. CNCjs is a web-based interface for CNC controllers that you will use to send the generated `.gcode` file to your plotter. It must be installed and running on the machine connected to your CNC plotter.

1. **Install Node.js:**
    Node.js version 14 or higher is recommended. You can download it from the [official Node.js website](https://nodejs.org/) or use a version manager like `nvm`.

2. **Install CNCjs:**
    Open your terminal or command prompt and install CNCjs globally using `npm`.

    ```bash
    npm install -g cncjs
    ```

    *Note: If you are not a root user, you may need to use `sudo` on Linux/macOS. If you do, use the `--unsafe-perm` flag as recommended by the CNCjs documentation:*

    ```bash
    sudo npm install --unsafe-perm -g cncjs
    ```

3. **Run the CNCjs Server:**
    With your CNC plotter connected to your computer via USB, run the following command to start the server:

    ```bash
    cncjs
    ```

    The server will start and listen on port 8000 by default.

4. **Configure the IP Address in `app.js`:**
    Open the `app.js` file and find the following code block. You **must** change the IP address `'http://192.168.228.232:8000'` to the IP address of the computer that is running CNCjs. If you are running everything on the same computer, you can use `localhost`.

    ```javascript
    $(".custom-btn2").click(function() {
        // Change this IP address to your CNCjs server's address
        window.open('http://<YOUR-CNCJS-IP-ADDRESS>:8000', '_blank');
    });
    ```

### 3. Frontend Usage

1. **Open the Application:**
    Simply open the `index.html` file in your web browser.

2. **Allow Microphone Access:**
    The browser will prompt you for permission to use your microphone. You must allow this for the speech recognition to work.

## How to Use

1. **Start Recognition:** Click the **Start** button. The button will change to "Stop" and the status will update to "Voice Recognition is on".
2. **Speak:** Dictate the text you want to convert into G-code. The transcribed text will appear in the text area in real-time.
3. **Stop Recognition:** Click the **Stop** button to pause the recognition.
4. **Convert to G-code:** Once your text is finalized in the text box, click the **Convert text to g-code** button.
5. **Review G-code:** The generated G-code will appear in the "G-code" text area on the right side of the screen.
6. **Save G-code:** Click the **Save** button to download the G-code as an `output.gcode` file to your computer.
7. **Send to CNC:**
    - Click the **Click to go to G-code sender** button. This will open the CNCjs interface in a new tab.
    - Inside CNCjs, connect to your CNC machine's serial port.
    - Load the `output.gcode` file you just saved.
    - Run the job to start plotting.