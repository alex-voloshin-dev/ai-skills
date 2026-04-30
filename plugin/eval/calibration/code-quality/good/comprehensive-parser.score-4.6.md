# Code Sample — Comprehensive CSV parser

```python
"""CSV parser with robust error handling and clear error messages."""

from dataclasses import dataclass
from typing import Iterator
import csv


class ParseError(Exception):
    """Raised when CSV parsing fails with details about location and cause."""
    pass


@dataclass
class Row:
    line_number: int
    data: dict


def parse_csv(filename: str) -> Iterator[Row]:
    """Parse CSV file line by line with error handling.
    
    Args:
        filename: Path to CSV file.
        
    Yields:
        Row objects with line number and parsed data.
        
    Raises:
        ParseError: If header row is malformed or data rows have wrong column count.
    """
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        if not reader.fieldnames:
            raise ParseError("CSV file is empty (no header row)")
        
        for line_num, row in enumerate(reader, start=2):  # start=2 (header is line 1)
            if not row or all(v is None for v in row.values()):
                # Skip empty rows
                continue
            
            missing_fields = [k for k, v in row.items() if v is None or v.strip() == '']
            if missing_fields:
                raise ParseError(
                    f"Line {line_num}: missing required fields: {missing_fields}"
                )
            
            yield Row(line_number=line_num, data=row)


# Tests
def test_parse_valid_csv(tmp_path):
    csv_file = tmp_path / "valid.csv"
    csv_file.write_text("name,email\\nAlice,alice@example.com\\nBob,bob@example.com")
    
    rows = list(parse_csv(str(csv_file)))
    assert len(rows) == 2
    assert rows[0].data['name'] == 'Alice'
    assert rows[1].line_number == 3

def test_parse_empty_file(tmp_path):
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("")
    
    with pytest.raises(ParseError, match="empty"):
        list(parse_csv(str(csv_file)))

def test_parse_missing_field(tmp_path):
    csv_file = tmp_path / "missing.csv"
    csv_file.write_text("name,email\\nAlice,alice@example.com\\nBob,")
    
    with pytest.raises(ParseError, match="Line 3.*missing required fields"):
        list(parse_csv(str(csv_file)))
```
