# SQL to Excel Converter

A web application that converts SQL database dump files into Excel spreadsheets.

## Features

- Upload SQL dump files through a web interface
- Automatically converts SQL tables to Excel spreadsheets
- Downloads all converted files as a ZIP archive
- Supports large SQL files
- Beautiful and user-friendly interface
- Progress indication during conversion

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd excel_sql_project
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the web server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Upload your SQL file and click "Convert to Excel"
4. Wait for the conversion to complete
5. Download the ZIP file containing your Excel spreadsheets

## Technical Details

- Built with Flask web framework
- Uses SQLite for temporary database storage
- Converts SQL tables to Excel using pandas
- Handles MySQL-specific syntax
- Supports various SQL file encodings

## Requirements

- Python 3.8 or higher
- See requirements.txt for Python package dependencies

## Error Handling

The application includes comprehensive error handling for:
- Invalid file types
- File size limits
- SQL syntax errors
- Encoding issues
- Database conversion errors

## License

MIT License
