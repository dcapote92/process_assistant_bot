import re
from branch import branchs
from pyrogram.types import KeyboardButton

branch_rows  = [ [KeyboardButton(branch) for branch in branchs[i:i+2]] for i in range(0, len(branchs), 2) ]


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
        
