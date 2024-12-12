import re

def get_str_from_dict(food_dict: dict):
    return ", ".join([f"{int(value)} {key}" for key, value in food_dict.items()])


def extract_sessionId(session_str: str):

    match = re.search(r"/sessions/(.*?)/contexts/",session_str)
    if match:
        extracted_string = match.group(1)
        return extracted_string

    return ""

if __name__=="__main__":
    # print(get_str_from_dict({"samosa":1,"pattis":2}))
    print(extract_sessionId("projects/foodx-isde/agent/sessions/8c6423f8-04e4-f944-8336-9eaa872eab49/contexts/ongoing-tracking"))

