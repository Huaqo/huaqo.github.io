import os
import markdown
import yaml
import shutil
from jinja2 import Environment, FileSystemLoader
from bs4 import BeautifulSoup


TARGET_DIR = "dist"
TEMPLATE_DIR = "src/templates"
NOTES_DIR = "src/notes"

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def list_local_markdown_files():
    files = []
    for file in os.listdir(NOTES_DIR):
        if file.endswith(".md"):
            files.append({
                "name": file,
                "path": os.path.join(NOTES_DIR, file)
            })
    return files


def fetch_local_markdown_file(file_info):
    with open(file_info["path"], "r", encoding="utf-8") as f:
        return f.read()


def copy_local_assets():
    src_assets = os.path.join("src", "assets")
    dst_assets = os.path.join(TARGET_DIR, "assets")

    if os.path.exists(dst_assets):
        shutil.rmtree(dst_assets)

    if os.path.exists(src_assets):
        shutil.copytree(src_assets, dst_assets)


def add_inline_style_to_images(html, style="width:100%; height:auto;"):
    soup = BeautifulSoup(html, "html.parser")
    for img in soup.find_all("img"):
        existing_style = img.get("style", "")
        if existing_style:
            img["style"] = existing_style + " " + style
        else:
            img["style"] = style
    return str(soup)


def process_content():
    ensure_dir(TARGET_DIR)

    files = list_local_markdown_files()
    files = sorted(files, key=lambda f: f["name"])


    page_links = ""
    for file in files:
        file_link = file["name"].replace(".md", ".html")
        file_name = file["name"].replace(".md", "")
        if file_name == "index":
            continue
        link = f'<a href="{file_link}">{file_name}</a><br>'
        page_links += link

    page_template = env.get_template("page.html")

    for file_info in files:
        filename = file_info["name"]
        md_content = fetch_local_markdown_file(file_info)
        html_content = markdown.markdown(md_content)
        html_content = add_inline_style_to_images(html_content)

        rendered_page = page_template.render(
            content=html_content,
            title=filename.replace(".md", ""),
            pages_links=page_links,
            asset_path="assets/"
        )

        html_filename = filename.replace(".md", ".html")
        with open(os.path.join(TARGET_DIR, html_filename), "w", encoding="utf-8") as f:
            f.write(rendered_page)


def build():
    process_content()
    copy_local_assets()


if __name__ == "__main__":
    build()
