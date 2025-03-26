from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
from utils.config import nlpModels
import csv, re, aiofiles
from typing import Literal


# ============================================================================================
# Prepare new data to train the model
# ============================================================================================
def convert_label_to_int(label_str):
    """
    Args:
        label_str: The string label ("TRIVIAL CHANGE!" or "SIGNIFICANT CHANGE!").

    Returns:
        0 if the label contains "TRIVIAL", 1 if it contains "SIGNIFICANT", -1 otherwise.
    """
    if "TRIVIAL" in label_str.upper():  # Case-insensitive check
        return 0
    elif "SIGNIFICANT" in label_str.upper():  # Case-insensitive check
        return 1
    else:
        return -1  # Or handle the default case as needed (e.g., raise an error)


def extract_colored_text(diff_str):
    """Extracts text within <span> tags with color red or green from a diff string.

    Args:
        diff_str: The diff string.

    Returns:
        A list of the extracted colored text strings.
    """
    red_matches = re.findall(r"<span style='color: red;'>(.*?)</span>", diff_str)
    green_matches = re.findall(r"<span style='color: green;'>(.*?)</span>", diff_str)
    return red_matches + green_matches


async def read_csv(
    filepath,
    mode: Literal[
        "data_with_label", "data_no_label", "numeric_label"
    ] = "numeric_label",
):
    try:
        async with aiofiles.open(
            filepath, "r", newline="", encoding="utf-8"
        ) as csvfile:
            reader = csv.reader(csvfile)  # returns an interator
            header = next(reader)  # skip the header if any
            # data = [dict(zip(header[2:], row[2:])) for row in reader]

            if mode == "data_with_label":
                data_with_label = [
                    [convert_label_to_int(row[2]), extract_colored_text(row[3])]
                    for row in reader
                    if any(keyword in row[2] for keyword in ["TRIVIAL", "SIGNIFICANT"])
                ]
                return data_with_label
            elif mode == "data_no_label":
                data_without_label = [
                    # extract_colored_text(row[3]) # returns List[List[str]]
                    ",".join(extract_colored_text(row[3]))  # returns List[str]
                    for row in reader
                    if any(keyword in row[2] for keyword in ["TRIVIAL", "SIGNIFICANT"])
                ]
                return data_without_label
            elif mode == "numeric_label":
                label = [
                    convert_label_to_int(row[2])
                    for row in reader
                    if any(keyword in row[2] for keyword in ["TRIVIAL", "SIGNIFICANT"])
                ]
                return label
    except FileNotFoundError as e:
        print(f"Error: File not found at {e}")
        return None


# ============================================================================================
# Train the model with the new data
# ============================================================================================
def train_model(your_data, output_path):
    train_examples = [
        InputExample(texts=[text1, text2], label=label)
        for label, text1, text2 in your_data
    ]
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=1)
    input_model = SentenceTransformer(nlpModels.ST_Model1.value)
    # for CosineSimilarityLoss we need a numeric label instead of string labels such as 'TRIVIAL' or 'SIGNIFICANT'
    train_loss = losses.CosineSimilarityLoss(model=input_model)
    input_model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=4,
        warmup_steps=100,
        output_path=output_path,
    )
