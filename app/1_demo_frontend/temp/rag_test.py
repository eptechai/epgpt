from dotenv import load_dotenv

load_dotenv()

import pytest
import json

from ai.framework.fsm.config import config_loader
from ai.framework.fsm.core.fsm_response_agent import FsmResponseAgent

from uc_plat_core.settings import BASE_DIR

# Note: SQL auth proxy required for this test!

def load_test_data(path):
    with open(path, "r") as file:
        data = json.load(file)
    return data


def do_test(question, expected):
    convo_json = '[{"role": "user", "content": ' + question + '}]'
    principles = FsmResponseAgent.get_rag_advice_principles(convo_json)
    assert expected.lower() in principles.lower()


test_data = load_test_data(BASE_DIR + "/ai/eval/rag_params.json")
conversation_template = config_loader.get_base_config()['CONVERSATION_TEMPLATES']['NONE']


def generate_test_cases(question_type):
    cases = []
    for item in test_data['rag_parameters']:
        if item['questions'][question_type]:
            cases.append((item['questions'][question_type], item['expected']))
    return cases


exact_wording_with_category_cases = generate_test_cases("exact_wording_with_category")
exact_wording_no_category_cases = generate_test_cases("exact_wording_no_category")
different_phrasing_cases = generate_test_cases("different_phrasing")


@pytest.mark.parametrize("question, expected", exact_wording_with_category_cases)
def test_exact_wording_with_category(question, expected):
    do_test(question, expected)


@pytest.mark.parametrize("question, expected", exact_wording_no_category_cases)
def test_exact_wording_no_category(question, expected):
    do_test(question, expected)


@pytest.mark.parametrize("question, expected", different_phrasing_cases)
def test_different_phrasing(question, expected):
    do_test(question, expected)


