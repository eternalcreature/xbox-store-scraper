import re
import yaml
import json
from datetime import datetime, timezone
import os
import requests
from bs4 import BeautifulSoup


def extract_available_on_section(text):
    pattern = r'"availableOn":\[[^\[\]]*\]'
    match = re.search(pattern, text)
    return match.group(0) if match else None


def extract_capabilities_section(text):
    pattern = r'"capabilities":\{[^{}]*\}'
    match = re.search(pattern, text)
    return match.group(0) if match else None


def extract_title_section(text):
    pattern = r'\],"title":"[^"]*"'
    match = re.search(pattern, text)
    if match:
        extracted = match.group(0)
        return extracted[10:]  # Remove the leading '],'
    return None


def has_non_empty_list(nested_dict):
    for value in nested_dict.values():
        if isinstance(value, dict):  # If the value is a nested dictionary, recurse
            if has_non_empty_list(value):
                return True
        elif isinstance(value, list):  # Check if the value is a list
            if value:  # Non-empty list evaluates to True
                return True
    return False


def sort_yaml(file_path):
    with open(file_path, "r") as file:
        content = file.read()

    sections = content.split("---")
    sections = [section.strip() for section in sections if section.strip()]
    sections.sort()
    sorted_content = "\n---\n".join(sections)
    with open(file_path, "w") as file:
        file.write(sorted_content)


def load_yaml(file_path):
    with open(file_path, "r") as file:
        return list(yaml.safe_load_all(file))


def compare_sections(existing_section, new_section):
    """
    Compares two sections of a YAML file and returns the differences.

    Args:
        existing_section (dict): The existing section from the main YAML.
        new_section (dict): The newly imported section.

    Returns:
        list[dict1,dict2]: Differences found in the new section.
    """
    differences = {}
    changes = {}
    for key, value in new_section.items():
        if (old_value := existing_section.get(key)) != value:
            differences[key] = value
            changes[key] = compare_lists(old_value, value)
    return [differences, changes]


def compare_lists(old_list, new_list):
    """
    Compares two lists and identifies items added and removed.

    Args:
        old_list (list): The original list.
        new_list (list): The updated list.

    Returns:
        dict: A dictionary with 'added' and 'removed' keys containing the respective items.
    """
    removed = [item for item in old_list if item not in new_list]
    added = [item for item in new_list if item not in old_list]
    return {"removed": removed, "added": added}


class LogBook:
    def __init__(self, yaml_file="data.yaml", url_file="urls.txt") -> None:
        time = str(datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S"))[:19]
        file_name = "log_" + time
        folder = "logs"
        self.file_path = os.path.join(folder, f"{file_name}.txt")
        os.makedirs(folder, exist_ok=True)
        with open(self.file_path, "w"):
            pass
        self.url_file = url_file
        self.yaml_file = yaml_file
        self.updated_games = []
        self.data = []
        self.load_urls()
        self.run_main_loop()

    def load_urls(self) -> None:
        with open(self.url_file, "r") as f:
            self.urls = f.readlines()
            self.urls = [url.strip() for url in self.urls]

    def run_main_loop(self) -> None:
        for i, url in enumerate(self.urls):
            response = requests.get(url)
            soup = BeautifulSoup(response.text, features="lxml")
            text = str(soup)
            title = extract_title_section(text)
            capabilities = extract_capabilities_section(text)
            available_on = extract_available_on_section(text)
            url = f'"url":["{url}"]'

            metadata = (
                "{"
                + title
                + ":{"
                + capabilities
                + ","
                + available_on
                + ","
                + url
                + "}}"
            )
            metadata = json.loads(metadata)
            self.update_yaml(title, metadata)

    def update_yaml(self, title, metadata):
        """
        Updates a section in the YAML file with new data.

        Args:
            file_path (str): Path to the YAML file.
            section_name (str): The name of the section to update.
            new_section (dict): The new section data.
        """
        documents = load_yaml(self.yaml_file)
        # Remove any surrounding quotes from the section_name
        title = title.strip('"').strip("'")
        for doc in documents:
            # Check if section_name exists in the document
            if title in doc:
                differences = compare_sections(doc[title], metadata[title])
                if differences[1]:
                    if has_non_empty_list(differences[1]):
                        changes = yaml.dump(differences[1], default_flow_style=False)
                        log = f"""Updated the entry for '{title}' with following changes: 
        {changes}\n\n"""
                        print(log)
                        with open(self.file_path, "a") as f:
                            f.write(log)

                        doc[title].update(differences[0])
                        self.updated_games.append(title)

                else:
                    print(f"No changes found for '{title}'.")
                break
        else:
            with open(self.file_path, "a") as a:
                a.write(f"Added the entry for {title}.\n\n")
                # Ensure the new_section only contains the desired section_name key
                self.updated_games.append(title)
                documents.append(metadata)

        with open(self.yaml_file, "w") as file:
            yaml.dump_all(documents, file)
