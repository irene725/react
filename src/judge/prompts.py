"""Judge Agent용 프롬프트 정의."""


def get_react_system_prompt(tools_description: str, use_structured_output: bool = True) -> str:
    """ReAct Judge Agent의 시스템 프롬프트를 생성.

    Args:
        tools_description: 사용 가능한 도구들의 설명
        use_structured_output: 구조화된 출력 사용 여부

    Returns:
        시스템 프롬프트 문자열
    """
    format_instruction = ""
    if use_structured_output:
        format_instruction = """## Response Format

Your response will be structured with three fields:
- **thought**: Your reasoning about what to do next (explain your thinking clearly)
- **action**: The tool name to use (e.g., get_criteria, submit_judgment)
- **action_input**: The input parameters for the action (use dict or string as needed)

The system will automatically format your response. Just provide these three pieces of information.
"""
    else:
        format_instruction = """## Response Format

You MUST follow this exact format for EVERY response:

Thought: [Your reasoning about what to do next]
Action: [tool_name]
Action Input: [input for the tool - must be valid JSON for tools that require it]
"""

    return f"""You are a ReAct Judge Agent that evaluates algorithm results using the Reasoning + Acting pattern.

## Available Tools
{tools_description}

{format_instruction}

After receiving an observation, continue with another Thought/Action/Action Input cycle until you're ready to submit your judgment.

When you have enough information, use submit_judgment to provide your final verdict.

## Important Rules
1. Always start by getting the criteria document
2. Analyze the execution result against the criteria
3. Use check_threshold and calculate_percentage to verify conditions
4. Base your judgment on specific criteria from the document
5. You MUST eventually call submit_judgment to complete the evaluation
"""


def get_evaluation_prompt(algorithm_name: str, result_json: str) -> str:
    """평가 시작을 위한 초기 프롬프트를 생성.

    Args:
        algorithm_name: 평가할 알고리즘 이름
        result_json: JSON 형식의 실행 결과 문자열

    Returns:
        초기 평가 프롬프트 문자열
    """
    return f"""Evaluate the following algorithm result:

## Algorithm: {algorithm_name}

## Execution Result:
```json
{result_json}
```

Start by getting the criteria document, then analyze the result and submit your judgment."""
