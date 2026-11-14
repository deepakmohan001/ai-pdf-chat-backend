
import re


# Common PDF section headings
SECTION_HEADINGS = {
    "summary",
    "profile",
    "skills",
    "technical skills",
    "experience",
    "work experience",
    "professional experience",
    "project highlights",
    "projects",
    "internship",
    "education",
    "certifications",
    "languages",
}


def is_section_heading(line):
    line = line.strip()

    # Check known section headings
    if line.lower().strip(" :") in SECTION_HEADINGS:
        return True

    # Check numbered headings (e.g., 1. API Requirement)
    if re.match(r"^\d+(\.\d+)*\.?\s+[A-Z]", line):
        return True

    return False


def split_text_into_chunks(text, chunk_size=500, overlap=50):

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between 0 and chunk_size - 1")

    # Step 1: Extract non-empty lines
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # Step 2: Group lines into sections
    sections = []
    current_section = []

    for line in lines:

        if is_section_heading(line):

            if current_section:
                sections.append(" ".join(current_section))

            current_section = [line]

        else:
            current_section.append(line)

    if current_section:
        sections.append(" ".join(current_section))

    # Step 3: Create chunks
    chunks = []
    current_words = []

    def save_chunk(words):
        if words:
            chunks.append(" ".join(words))

    def split_large_section(words):
        step = chunk_size - overlap

        for start in range(0, len(words), step):
            chunk_words = words[start:start + chunk_size]
            save_chunk(chunk_words)

    for section in sections:

        section_words = section.split()

        # Handle sections larger than chunk_size
        if len(section_words) > chunk_size:

            if current_words:
                save_chunk(current_words)
                current_words = []

            split_large_section(section_words)
            continue

        # Check whether the section fits in the current chunk
        if len(current_words) + len(section_words) <= chunk_size:

            current_words.extend(section_words)

        else:
            # Save the current chunk
            save_chunk(current_words)

            # Keep overlap from the previous chunk
            overlap_words = (
                current_words[-overlap:]
                if overlap
                else []
            )

            current_words = overlap_words + section_words

    # Step 4: Save remaining content
    save_chunk(current_words)

    return chunks
