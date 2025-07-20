from nodes import extract_mermaid_from_markdown, convert_mmd_to_png
import os

directory_path = "./flowcharts"

if __name__ == "__main__":
    # Ensure output directories exist
    os.makedirs("Mermaids", exist_ok=True)
    os.makedirs("images", exist_ok=True)

    # Process each .md file in the flowcharts directory
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if filename.endswith(".md") and os.path.isfile(file_path):
            # Extract Mermaid content from the .md file
            with open(file_path, "r") as f:
                md_content = f.read()
            extracted_content = extract_mermaid_from_markdown(md_content)

            # Save the extracted content as .mmd in Mermaids directory
            new_filename = filename.replace(".md", ".mmd")
            new_file_path = os.path.join("Mermaids", new_filename)
            with open(new_file_path, "w") as f:
                f.write(extracted_content)

            # Convert .mmd to .png and save in images directory
            output_file = os.path.join(
                "images", new_filename.replace(".mmd", ".png")
            )
            convert_mmd_to_png(new_file_path, output_file)
            print(f"Converted {new_file_path} to {output_file}")
