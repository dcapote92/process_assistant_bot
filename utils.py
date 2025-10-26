import re
from branch import branchs

def find_branch(text):
    """Find a branch based on the number on text

    Args:
        text (str): message.text

    Returns:
        str: branch number and name
    """
    number = re.findall(r'\d+', text)
    for branch in branchs:
        if number[0] in branch:
            return branch