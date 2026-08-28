# RIS Pre-Screener

This tool helps you make a first, keyword-based decision about articles in a
RIS file. It works locally on your computer and does not upload your literature
data anywhere.

## Easiest way to use it

### 1. Install Python

Download Python 3.10 or newer from <https://www.python.org/downloads/>.
During installation on Windows, enable **Add Python to PATH**.

### 2. Download this repository

On GitHub, click **Code → Download ZIP** and unzip the downloaded folder.

### 3. Open a terminal in the unzipped folder

- **Windows:** right-click the folder and choose **Open in Terminal**
- **macOS:** open Terminal, type `cd ` (including the space), drag the folder
  into the Terminal window, and press Enter

### 4. Install the application

Run these commands:

```bash
python -m venv .venv
```

Activate the environment:

```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

Then install the required packages:

```bash
pip install -e .
```

### 5. Start the application

```bash
streamlit run app.py
```

A browser window opens automatically. If it does not, copy the local address
shown in the terminal (usually `http://localhost:8501`) into your browser.

## Using the application

1. Choose your `.ris` file.
2. Enter a name for each keyword group, for example `Population` or
   `Intervention`.
3. Enter one keyword per line in each group.
4. Leave **Required** enabled when every included record must match that group.
5. Click **Add keyword group** when you need another group.
6. Optionally add exclusion keywords, one per line.
7. Click **Run screening**.
8. Download the INCLUDE CSV or the complete decision list.

Group names must be unique and every group must contain at least one keyword.
The app searches the title and abstract. Keywords within a group use OR;
required groups use AND. Exclusion keywords always take priority.

## Troubleshooting

If `python` is not recognized, try `python3` instead. If the browser page is
blank, stop the terminal command with `Ctrl+C` and start it again with
`streamlit run app.py`.

## For developers

The reusable code is in `src/ris_prescreener/`, tests are in `tests/`, and the
project can also be run with Docker:

```bash
docker build -t ris-pre-screener .
docker run --rm -p 8501:8501 ris-pre-screener
```

## Privacy, license, and support

Do not commit RIS files, CSV exports, notebooks, credentials, or personal
research information. See [SECURITY.md](SECURITY.md) for safe usage and
vulnerability reporting.

This project is released under the [MIT License](LICENSE).

If this tool saves you time, you can support development here:

[Buy me a coffee](https://www.buymeacoffee.com/vincentlill)

