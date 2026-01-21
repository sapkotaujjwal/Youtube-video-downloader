import re

def srt_to_text(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove subtitle numbers
    content = re.sub(r"^\d+\s*$", "", content, flags=re.MULTILINE)

    # Remove timestamps
    content = re.sub(
        r"\d{2}:\d{2}:\d{2},\d{3}\s-->\s\d{2}:\d{2}:\d{2},\d{3}",
        "",
        content
    )

    # Remove empty lines and extra spaces
    lines = [line.strip() for line in content.splitlines() if line.strip()]

    # Join into paragraph
    text = " ".join(lines)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)

    print("✅ Conversion complete!")


if __name__ == "__main__":
    input_srt = "inustrial revolution.srt"     # your SRT file
    output_txt = "output.txt"      # clean text file
    srt_to_text(input_srt, output_txt)
