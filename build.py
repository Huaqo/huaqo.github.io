import os
import markdown
import yaml
import shutil
from jinja2 import Environment, FileSystemLoader


SOURCE_DIR = "src/blog"
TARGET_DIR = "."
POST_DIR = "blog"
TEMPLATE_DIR = "src/templates"

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def extract_metadata_and_content(full_content):
    parts = full_content.split('---')
    if len(parts) < 3:
        return {}, full_content
    metadata = yaml.safe_load(parts[1])
    content = '---'.join(parts[2:])
    return metadata, content.strip()

def process_content(all_pages_metadata):
    for filename in os.listdir(SOURCE_DIR):
        if filename.endswith(".md"):
            with open(os.path.join(SOURCE_DIR, filename), 'r') as f:
                full_content = f.read()
                metadata, md_content = extract_metadata_and_content(full_content)

                html_content = markdown.markdown(md_content)
                
                template = env.get_template('post.html')
                output = template.render(
                    title=metadata.get('title', 'Untitled'), 
                    date=metadata.get('date', ''),
                    description=metadata.get('description', ''),
                    tags=metadata.get('tags', ''),
                    content=html_content)
                
                html_filename = filename.replace(".md", ".html")
                with open(os.path.join(POST_DIR, html_filename), 'w') as f:
                    f.write(output)
                
                page_info = metadata.copy()
                page_info['url'] = filename.replace(".md", ".html")
                all_pages_metadata.append(page_info)

def generate_index_page(pages):
    template = env.get_template('index.html')

    try:
        output = template.render(pages=pages)
    except Exception as e:
        print(f"Error during template rendering: {e}")

    with open(os.path.join(TARGET_DIR, 'index.html'), 'w') as f:
        f.write(output)

def build():
    ensure_dir(TARGET_DIR)
    ensure_dir(POST_DIR)
    all_pages_metadata = []
    process_content(all_pages_metadata)
    generate_index_page(all_pages_metadata)



if __name__ == "__main__":
    build()
