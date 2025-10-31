import fitz

def chunk_file_fixed(file_path, chunk_size=500, overlap=50):

    try:
        if file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

        elif file_path.endswith('.pdf'):
            content = ""
            with fitz.open(file_path) as doc:
                for page in doc:
                    text = page.get_text("text")
                    if text:
                        content += text + "\n"
        else:
            raise ValueError("Unsupported file type. Use .txt or .pdf")
        
        content = content.strip()
        if not content:
            print("No readable content found.")
            return []

        chunks = []
        start = 0
        while start < len(content):
            end = start + chunk_size
            chunk = content[start:end]
            chunks.append(chunk.strip())
            start += chunk_size - overlap
        
        return chunks

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    except Exception as e:
        print(f"Exception occurred: {e}")
        return []

def chunk_file_delimiter(file_path, delimiter="\n\n"):

    try:
        if file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

        elif file_path.endswith('.pdf'):
            content = ""
            with fitz.open(file_path) as doc:
                for page in doc:
                    text = page.get_text("text")
                    if text:
                        content += text + "\n"
        else:
            raise ValueError("Unsupported file type. Use .txt or .pdf")
        
        content = content.strip()
        if not content:
            print("No readable content found.")
            return []

        chunks = [chunk.strip() for chunk in content.split(delimiter) if chunk.strip()]
        
        return chunks

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    except Exception as e:
        print(f"Exception occurred: {e}")
        return []
